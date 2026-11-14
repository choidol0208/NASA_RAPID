#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14). Catalog values are AI-extracted from the PSI
# records in data/psi/ and must be checked by a person (verification_status column).
"""Build the two-level experiment catalog from the PSI records and experimental tables.

Usage:
    python3 scripts/build_catalog.py

Reads   data/psi/manifest.json, data/psi/catalog/PSI-*.json,
        data/psi/experimental_tables/*.csv
Writes  data/catalog/investigations.csv   (one row per PSI investigation, 24 rows)
        data/catalog/configurations.csv   (one row per test configuration, the scoring unit)
        data/catalog/data_dictionary.csv  (column meanings in Korean, allowed values)

Rules followed (see AGENTS.md section 5):
- Numbers come from the PSI experimental tables or the PSI record text. The column
  `atmosphere_basis` says which. Nothing is filled from general knowledge: if the
  record does not state a value, the cell stays empty.
- Classification columns (tier, fire_safety_role, research_focus, fire_scenario_tags,
  fuel_class, thermal_regime, sooting_tendency) are the team's judgement, not NASA's.
- Every row starts as verification_status = ai_extracted.
"""
import csv
import io
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PSI = os.path.join(ROOT, "data", "psi")
OUT = os.path.join(ROOT, "data", "catalog")
TABLES = os.path.join(PSI, "experimental_tables")
COLLECTED_ON = "2026-11-14"
ATM_KPA = 101.325
MMHG_KPA = 0.133322
BAR_KPA = 100.0


# ----------------------------------------------------------------------------- helpers
def load_table(name):
    raw = open(os.path.join(TABLES, name), "rb").read()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    rows = [r for r in csv.reader(io.StringIO(text)) if any(c.strip() for c in r)]
    return rows[0], rows[1:]


def num(s):
    s = str(s).strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def rng(values, scale=1.0, nd=1):
    vals = [v * scale for v in values if v is not None]
    if not vals:
        return "", ""
    return round(min(vals), nd), round(max(vals), nd)


def col(rows, j):
    return [r[j] if j < len(r) else "" for r in rows]


def unique_rows(rows):
    """Drop rows that repeat an earlier row cell for cell (same test entered twice).
    Returns (distinct rows, number dropped). Same rule as the data pipeline."""
    seen, out = set(), []
    for r in rows:
        k = tuple(c.strip() for c in r)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out, len(rows) - len(out)


BASS2_TUNNEL_MAX_CMS = 40.0  # PSI-25 record, approach: "airflow speeds up to 40 cm/s"


def bass2_air(cell):
    """Air speeds (cm/s) in one BASS-II 'Air display' cell, as the team reads the column:
    - numbers outside brackets only: bracketed numbers, "max(47)" included, and numbers
      after "pot"/"pots" are fan or potentiometer readings (the table's own convention);
    - nothing above the 40 cm/s that the PSI-25 record gives as the tunnel's limit: fan
      readings (40.5 to 62) also appear in the air column (rows 53, 54, 63, 117)."""
    s = re.sub(r"\([^)]*\)", " ", cell)
    s = re.split(r"(?i)\bpots?\b", s)[0]
    vals = [float(x) for x in re.findall(r"\d+\.?\d*", s)]
    return [v for v in vals if v <= BASS2_TUNNEL_MAX_CMS]


def bass2_family(material):
    """Sample family of one BASS-II row ('Fuel Sample Material'); one configuration per family."""
    m = material.lower()
    if "sibal" in m:
        return "sibal"
    if "nomex" in m:
        return "nomex"
    if "rod" in m:
        return "rod"
    if "spher" in m or "wax" in m or "candle" in m:
        return "other"
    if "film" in m or "micron" in m or re.search(r"0\.[1-4] mm", m):
        return "film"
    return "slab"


# Configuration id -> BASS-II sample family (the fl("B2_<family>", ...) keys in CONFIGS below).
BASS2_CONFIG_FAMILY = {"BASS-II-C01": "film", "BASS-II-C02": "slab", "BASS-II-C03": "rod",
                       "BASS-II-C04": "sibal", "BASS-II-C05": "nomex", "BASS-II-C06": "other"}


# ----------------------------------------------------------------- computed table facts
def facts():
    f = {}
    # FLEX (PSI-69): columns O/N/CO/He are O2/N2/CO2/He mole fractions (NASA/TP-2015-216046).
    _, rows = load_table("PSI-69_Experimental table_FLEX.csv")
    for fuel in ("Methanol", "Heptane"):
        rs = [r for r in rows if r[4].strip() == fuel]
        p = [num(r[5]) for r in rs if (num(r[5]) or 0) > 0]
        f[f"FLEX_{fuel}"] = dict(
            n=len(rs),
            o2=rng([num(r[6]) for r in rs], 100, 0),
            p=rng(p, MMHG_KPA, 1),
            co2=rng([num(r[8]) for r in rs], 100, 0),
            he=rng([num(r[9]) for r in rs], 100, 0),
            d0=rng([num(r[10]) for r in rs], 1, 2),
            end=Counter(r[14].strip() for r in rs),
        )
    # CFI (PSI-39)
    _, rows = load_table("PSI-39_Experimental table_CFI.csv")
    rows, cfi_dup = unique_rows(rows)
    patm = [num(re.sub(r"[^\d.]", "", r[4])) for r in rows]
    f["CFI"] = dict(n=len(rows), dup=cfi_dup, p=rng(patm, ATM_KPA, 1),
                    o2=rng([num(r[5]) for r in rows], 100, 0),
                    he=rng([num(r[7]) for r in rows], 100, 0))
    # Flame Design (PSI-10)
    _, rows = load_table("PSI-10_Experimental table_Flame Design_Normal Flame.csv")
    f["FD_normal"] = dict(n=len(rows), o2=rng([num(r[8]) for r in rows], 100, 1),
                          p=rng([num(r[10]) for r in rows], ATM_KPA, 1),
                          fuels=sorted(set(r[2].strip() for r in rows)))
    _, rows = load_table("PSI-10_Experimental table_Flame Design_Inverse Flame.csv")
    f["FD_inverse"] = dict(n=len(rows), o2=rng([num(r[3]) for r in rows], 100, 1),
                           p=rng([num(r[9]) for r in rows], ATM_KPA, 1),
                           xf=rng([num(r[7]) for r in rows], 100, 0))
    # CFI-G (PSI-159)
    _, rows = load_table("PSI-159_Experimental table_CFI-G_Normal Flames.csv")
    f["CFIG_normal"] = dict(n=len(rows), o2=rng([num(r[5]) for r in rows], 100, 1),
                            p=rng([num(r[7]) for r in rows], BAR_KPA, 1),
                            fuels=sorted(set(r[2].strip() for r in rows)))
    _, rows = load_table("PSI-159_Experimental table_CFI-G_Inverse Flames.csv")
    f["CFIG_inverse"] = dict(n=len(rows), o2=rng([num(r[7]) for r in rows], 100, 0),
                             p=rng([num(r[6]) for r in rows], BAR_KPA, 1),
                             fuels=sorted(set(r[2].strip().lower() for r in rows)))
    # SAME-R (PSI-101)
    _, rows = load_table("PSI-101_Experimental table_SAME-R.csv")
    f["SAMER"] = dict(n=len(rows), v=rng([num(r[4]) for r in rows], 1, 1),
                      age=rng([num(r[9]) for r in rows], 1, 0),
                      mats=sorted(set(r[0].strip() for r in rows)))
    # SPICE (PSI-107)
    _, rows = load_table("PSI-107_Experimental table_Spice.csv")
    rows, spice_dup = unique_rows(rows)
    air = [num(r[8]) for r in rows if len(r) > 8]
    f["SPICE"] = dict(n=len(rows), dup=spice_dup, fuels=sorted(set(r[3].strip() for r in rows)),
                      air=rng([a for a in air if a is not None and a >= 0], 1, 2),
                      air_negative=sorted(a for a in air if a is not None and a < 0))
    # ACME day tables: sum of "Flames Ignited"
    for key, name, j in (("BRE", "PSI-20_Experimental table_ACME BRE.csv", 6),
                         ("CLD", "PSI-21_Experimental table_CLD Flame.csv", 6),
                         ("EFIELD", "PSI-22_Experimental table_ACME E-FIELD Flames.csv", 8),
                         ("SFLAME", "PSI-23_Experimental table_ACME s-Flame.csv", 7)):
        _, rows = load_table(name)
        f[key] = dict(flames=int(sum(num(r[j]) or 0 for r in rows if j < len(r))))
    # BASS-II (PSI-25): group the 129 tests by sample family
    _, rows = load_table("PSI-25_Experimental table_BASS-II.csv")
    groups = {}
    for r in rows:
        groups.setdefault(bass2_family(r[5]), []).append(r)
    for g, rs in groups.items():
        air = [a for r in rs for a in bass2_air(r[8])]
        f[f"B2_{g}"] = dict(n=len(rs), o2=rng([num(r[11]) for r in rs], 1, 1),
                            air=rng(air, 1, 1), pis=sorted(set(r[0] for r in rs)))
    # BASS (PSI-26): sample families (table has no flow or O2 columns)
    _, rows = load_table("PSI-26_Experimental table_BASS.csv")

    def bfam(m):
        m = m.lower()
        if "sibal" in m:
            return "sibal"
        if "nomex" in m or "ultem" in m:
            return "sheet"
        if "wax" in m or "candle" in m:
            return "wax"
        if "sphere" in m:
            return "sphere"
        if "soot" in m:
            return "skip"
        return "slab"

    bc = Counter(bfam(r[5]) for r in rows)
    for g, n in bc.items():
        f[f"B1_{g}"] = dict(n=n)
    return f


F = facts()


def fl(key, field, i):
    v = F[key][field]
    return v[i] if isinstance(v, tuple) else v


# ------------------------------------------------------------------- investigation rows
# objectives / key_findings are short English paraphrases of the PSI record text.
INV = {
 "PSI-10": dict(investigation_id="ACME-FLAME-DESIGN", project_group="ACME", tier=3,
    objectives="Soot-inception and extinction limits of normal and inverse spherical diffusion flames (ethylene, methane/propane) versus flow rate, stoichiometric mixture fraction, inert dilution and pressure.",
    research_focus="smoke_soot; extinction_limit; flame_structure", fire_safety_role="fundamental",
    fire_scenario_tags="gas_leak; high_oxygen", has_1g_comparison="",
    key_findings="Record lists objectives and hypotheses only; results are in 33 linked publications (e.g., radiative extinction of spherical diffusion flames).",
    notes="Hypothesis: spherical diffusion flames extinguish when peak temperature falls below 1130 K. License field empty in PSI record."),
 "PSI-20": dict(investigation_id="ACME-BRE", project_group="ACME", tier=1,
    objectives="Burning Rate Emulator: gas burner that emulates condensed-phase fuels to map quiescent microgravity burning and extinction versus material properties, in spacecraft-candidate atmospheres.",
    research_focus="burning_rate; extinction_limit; flammability_boundary", fire_safety_role="prevention",
    fire_scenario_tags="cabin_material; high_oxygen; quiescent_ambient", has_1g_comparison="Y",
    key_findings="Quasi-steady burning emulating condensed fuels (e.g., PMMA, nylon) was seen without airflow, notably in elevated-oxygen atmospheres; in 21% O2 such flames self-extinguished in a short time (record calls results preliminary).",
    notes="Atmospheres named in objectives: 14.7 psia/21% O2, 10.2 psia/26.5% O2, 8.2 psia/34% O2. Table lists O2 only; pressures not tabulated."),
 "PSI-21": dict(investigation_id="ACME-CLD", project_group="ACME", tier=3,
    objectives="Coflow laminar diffusion flames of methane and ethylene at extreme fuel dilution: flame shape, lift-off, temperature, extinction limits and sooting behaviour for model validation.",
    research_focus="flame_structure; smoke_soot; extinction_limit", fire_safety_role="fundamental",
    fire_scenario_tags="gas_leak", has_1g_comparison="Y",
    key_findings="Record lists objectives only; results in 18 linked publications (including microgravity versus normal-gravity comparisons).",
    notes="Fuel concentration listed for ignited flames only."),
 "PSI-22": dict(investigation_id="ACME-E-FIELD", project_group="ACME", tier=2,
    objectives="Electric-field effects (up to 10 kV) on laminar gas-jet and coflow diffusion flames: ion current, dynamic response, soot and near-limit lifted flames.",
    research_focus="flame_structure; smoke_soot", fire_safety_role="fundamental",
    fire_scenario_tags="", has_1g_comparison="",
    key_findings="Record lists objectives only; ion-driven convection lets an electric field act like buoyancy (relevant as a partial-gravity analog).",
    notes="Record states the work does not serve space applications directly."),
 "PSI-23": dict(investigation_id="ACME-S-FLAME", project_group="ACME", tier=3,
    objectives="Transient and quasi-steady spherical diffusion flames of H2/CH4/C2H4 with N2 or He dilution: structure, convective/kinetic and radiative extinction limits, pulsating instabilities.",
    research_focus="flame_structure; extinction_limit", fire_safety_role="fundamental",
    fire_scenario_tags="gas_leak", has_1g_comparison="",
    key_findings="Record lists objectives only; results in 44 linked publications.",
    notes="Atmosphere ~1 atm; pressure rises and O2% drops with vitiation (table note)."),
 "PSI-25": dict(investigation_id="BASS-II", project_group="BASS", tier=1,
    objectives="Ignition, flame growth, spread and extinction limits of solid fuels (PMMA films/slabs/rods, SIBAL and Nomex fabrics) in low-speed forced flow at reduced O2, to bridge NASA-STD-6001 Test 1 and real microgravity flammability.",
    research_focus="ignition; flame_spread; extinction_limit; flammability_boundary", fire_safety_role="prevention",
    fire_scenario_tags="cabin_material", has_1g_comparison="Y",
    key_findings="Hypothesis tested: with adequate ventilation, materials burn as well or better in microgravity than in normal gravity, so the upward 1g test may not be conservative in space. Linked papers report a microgravity flammability boundary for PMMA rods and radiative extinction at low opposed-flow speed.",
    notes="Wind tunnel flow up to 40 cm/s (record). The 'Air display' column also holds fan readings above 40 (rows 53, 54, 63, 117, 121), which are not read as air speed; the highest air value is 38.5 (row 72). O2 lowered below 21% by adding N2. 'Air display' is cm/s (team check of PSI-25 ReadMe)."),
 "PSI-26": dict(investigation_id="BASS", project_group="BASS", tier=1,
    objectives="Flammability of practical, thicker solids (SIBAL and Nomex fabric, PMMA slabs and spheres, wax, Ultem) in concurrent and opposed flow up to 40 cm/s, and effectiveness of an inert gas (N2) extinguishing agent.",
    research_focus="flame_spread; suppression; extinction_limit", fire_safety_role="prevention; suppression",
    fire_scenario_tags="cabin_material", has_1g_comparison="",
    key_findings="Record stresses radiative heat emission from the flame as critical for first-order heat-release models; nitrogen was used as the flame suppressant.",
    notes="Experimental table lists sample material only (no flow or O2 columns)."),
 "PSI-39": dict(investigation_id="CFI", project_group="CIR-MDCA droplets", tier=2,
    objectives="Cool-flame combustion of n-dodecane and n-dodecane/iso-dodecane droplets at 0.5–5 atm, with helium dilution; droplet size, extinction and soot.",
    research_focus="extinction_limit; flame_structure", fire_safety_role="fundamental",
    fire_scenario_tags="liquid_leak", has_1g_comparison="",
    key_findings="Record lists objectives only; linked papers address cool-flame supported droplet burning and extinction.",
    notes="Record objective text says 0.25–5 atm and approach says 0.25–0.5 atm; table shows 0.5–5 atm."),
 "PSI-47": dict(investigation_id="DAFT", project_group="SAME", tier=2,
    objectives="Risk reduction for SAME: verify that a modified TSI P-Trak particle counter works in microgravity, compared with a DustTrak, using Arizona Road Dust aerosol standards.",
    research_focus="detection", fire_safety_role="detection",
    fire_scenario_tags="dust", has_1g_comparison="",
    key_findings="Record lists objectives and hypotheses only (instrument verification, no combustion).",
    notes="Covers DAFT and DAFT-2."),
 "PSI-60": dict(investigation_id="SPICE-ANALYSIS", project_group="SPICE", tier=3,
    objectives="Ground analysis of SPICE images: soot temperature and volume fraction from 1600+ raw images plus detailed soot modelling, to explain 1g versus 0g soot differences.",
    research_focus="smoke_soot", fire_safety_role="fundamental",
    fire_scenario_tags="gas_leak", has_1g_comparison="Y",
    key_findings="Record lists objectives and hypothesis (microgravity flames longer, cooler, sootier); results in 1 linked publication.",
    notes="Ground investigation reusing SPICE flight data; investigation_id assigned by team."),
 "PSI-62": dict(investigation_id="BASS-FGM-MODEL", project_group="BASS", tier=3,
    objectives="Ground modelling of concurrent flame spread over solids with unsteady flamelet-generated manifolds, validated against BASS/BASS-II imagery (two-colour tomography).",
    research_focus="flame_spread; flammability_boundary", fire_safety_role="prevention",
    fire_scenario_tags="cabin_material", has_1g_comparison="",
    key_findings="Record targets reproducing the 'Goldilocks' flammability zone reported by Olson and Ferkul; results in 4 linked publications.",
    notes="Ground investigation; investigation_id assigned by team."),
 "PSI-68": dict(investigation_id="FLEX-2", project_group="CIR-MDCA droplets", tier=2,
    objectives="Extend FLEX to practical and bi-component fuel droplets, droplet arrays, sooting and extinction boundaries. Atmosphere: 0.5 to 3.0 atm and O2 mole fraction 0.1 to 0.4 (PSI-68 record, approach); the planned test matrix (PSI table) lists 0.5, 1.0, 1.5, 2.0 or 3.0 atm and O2 mole fraction 0.17, 0.21, 0.25 or 0.3.",
    research_focus="burning_rate; extinction_limit; smoke_soot", fire_safety_role="fundamental",
    fire_scenario_tags="liquid_leak", has_1g_comparison="",
    key_findings="Record lists objectives only; results in 48 linked publications.",
    notes="Experimental table is a test matrix (planned ranges), not per-test results."),
 "PSI-69": dict(investigation_id="FLEX", project_group="CIR-MDCA droplets", tier=1,
    objectives="Flammability limits (limiting oxygen index) of methanol and heptane droplets and effectiveness of gaseous suppressants (CO2, He) versus pressure.",
    research_focus="extinction_limit; flammability_boundary; suppression; burning_rate", fire_safety_role="suppression; prevention",
    fire_scenario_tags="liquid_leak", has_1g_comparison="Y",
    key_findings="",  # filled below from the table
    notes="Table columns O/N/CO/He initial ambient composition are O2/N2/CO2/He; 'Burning rate; mm' is mm^2/s (NASA/TP-2015-216046)."),
 "PSI-98": dict(investigation_id="SAFFIRE-I", project_group="Saffire", tier=1,
    objectives="Large-scale fire growth in low gravity: 0.94 m x 0.4 m SIBAL fabric burned in a Cygnus cargo vehicle after it left the ISS, and comparison of low-g flammability with NASA's 1g screening test.",
    research_focus="flame_spread; flammability_boundary", fire_safety_role="prevention",
    fire_scenario_tags="cabin_material", has_1g_comparison="",
    key_findings="Two SIBAL samples at 20 cm/s: concurrent-flow test burned 420 s, opposed-flow test 70 s (table).",
    notes="Record investigation dates (2001-2008) are identical to SAME (PSI-102) and look like a record error; verify. Table labels length 40.6 cm and width 94 cm (record says 0.94 m long, 0.4 m wide); thickness listed as 0.37 cm while Saffire-II lists SIBAL as 0.37 mm."),
 "PSI-99": dict(investigation_id="SAFFIRE-II", project_group="Saffire", tier=1,
    objectives="Ignition and flammability of nine 5 cm x 29 cm samples (silicone, SIBAL, PMMA, PMMA with Nomex) in a Cygnus vehicle, with 1g comparison data.",
    research_focus="ignition; flame_spread; flammability_boundary", fire_safety_role="prevention",
    fire_scenario_tags="cabin_material", has_1g_comparison="Y",
    key_findings="At 20 cm/s and ~21.5 to ~22.1% O2 (table), silicone samples did not sustain burning in microgravity although some burned fully in 1g; SIBAL spread concurrently at 2.1–2.6 mm/s over the full 29 cm (table).",
    notes="Record says 20 or 30 cm/s; table lists 20 cm/s for all samples. O2 derived from CO2 production (table note 1)."),
 "PSI-100": dict(investigation_id="SAFFIRE-III", project_group="Saffire", tier=1,
    objectives="Repeat of the large-scale SIBAL fire at a higher flow of 30 cm/s, concurrent and opposed, in a Cygnus vehicle.",
    research_focus="flame_spread; flammability_boundary", fire_safety_role="prevention",
    fire_scenario_tags="cabin_material", has_1g_comparison="",
    key_findings="Record lists objectives only.",
    notes="Table thickness '.33 cm' (unit to verify against Saffire-II '0.37 mm'); O2 not tabulated."),
 "PSI-101": dict(investigation_id="SAME-R", project_group="SAME", tier=1,
    objectives="Size of smoke particles from overheated spacecraft materials (Kapton, silicone, lampwick, Teflon, Pyrell foam) in low gravity, with wider heating and no-flow conditions.",
    research_focus="smoke_soot; detection", fire_safety_role="detection",
    fire_scenario_tags="wire_overheat; smoldering", has_1g_comparison="Y",
    key_findings="66 test points flown 16 Jul–9 Sep 2010; post-flight ground tests validated the lognormal size-distribution assumption (record).",
    notes="Table has 109 rows including repeat ('a') runs."),
 "PSI-102": dict(investigation_id="SAME", project_group="SAME", tier=1,
    objectives="Size distribution of smoke particles from overheated spacecraft materials in low gravity, related to smoke generation and transport, for spacecraft smoke-detector design.",
    research_focus="smoke_soot; detection", fire_safety_role="detection",
    fire_scenario_tags="wire_overheat; smoldering", has_1g_comparison="Y",
    key_findings="Record lists hypotheses (larger smoke particles expected in microgravity) and methods; results in 16 linked publications.",
    notes="Thermophoretic sampler grids were contaminated (stated in SAME-R record)."),
 "PSI-106": dict(investigation_id="SLICE", project_group="MSG flow duct", tier=2,
    objectives="Structure and lift-off stability of laminar coflow jet diffusion flames (methane, ethane, ethylene, N2-diluted) versus burner diameter and coflow speed.",
    research_focus="flame_structure", fire_safety_role="fundamental",
    fire_scenario_tags="gas_leak", has_1g_comparison="Y",
    key_findings="Record lists objectives; more than 4,000 high-resolution images captured across 13 test sessions.",
    notes="Uses the SPICE fan-driven flow duct in the MSG."),
 "PSI-107": dict(investigation_id="SPICE", project_group="MSG flow duct", tier=2,
    objectives="Laminar smoke points of non-buoyant jet diffusion flames (ethylene, propane, propylene mixtures, methane) versus burner diameter and coflow speed.",
    research_focus="smoke_soot; flame_structure", fire_safety_role="fundamental",
    fire_scenario_tags="gas_leak", has_1g_comparison="Y",
    key_findings="526 flames studied (record); burner diameters 0.41, 0.76, 1.6 mm; coflow 5.4–65 cm/s.",
    notes="Table has 469 rows, 34 of them exact repeats of an earlier row (435 distinct); the air rate column runs 0.66–85.28 cm/s (after 8 negative cells), wider than the record's 5.4–65 cm/s."),
 "PSI-115": dict(investigation_id="SAME-SIM", project_group="SAME", tier=3,
    objectives="Numerical simulation (DNS) of pyrolysis smoke particle growth (dibutyl phthalate) in 1g and microgravity in a SAME-like geometry.",
    research_focus="smoke_soot; detection", fire_safety_role="detection",
    fire_scenario_tags="smoldering", has_1g_comparison="Y",
    key_findings="Record lists objectives and approach; no linked publications.",
    notes="Ground investigation; investigation_id assigned by team."),
 "PSI-117": dict(investigation_id="COOLFLAME-CFD", project_group="CIR-MDCA droplets", tier=3,
    objectives="3D CFD (OpenFOAM) of n-alkane droplet cool flames using FLEX data: effect of external thermal/convective perturbations on ignition, oscillation, transition and extinction.",
    research_focus="extinction_limit; flame_structure", fire_safety_role="fundamental",
    fire_scenario_tags="liquid_leak", has_1g_comparison="",
    key_findings="Record lists approach; results in 10 linked publications.",
    notes="Ground investigation; investigation_id assigned by team."),
 "PSI-142": dict(investigation_id="COOLFLAME-COUNTERFLOW", project_group="CIR-MDCA droplets", tier=3,
    objectives="Ground counterflow experiments and simulations (ozone-sensitised) to map cool-flame flammability and extinction limits, building on FLEX observations.",
    research_focus="extinction_limit; flame_structure", fire_safety_role="fundamental",
    fire_scenario_tags="", has_1g_comparison="",
    key_findings="Record: warm flames show a double reaction-zone structure; at elevated pressure the flammable region of warm and cool flames expands.",
    notes="Ground laboratory investigation; table is a list of figures in publications. investigation_id assigned by team."),
 "PSI-159": dict(investigation_id="ACME-CFI-G", project_group="ACME", tier=1,
    objectives="Cool diffusion flames of ethane, propane and butane on spherical porous burners, normal and inverse, over a wide range of stoichiometric mixture fraction, flame temperature and pressure.",
    research_focus="flame_structure; extinction_limit", fire_safety_role="fundamental; prevention",
    fire_scenario_tags="high_oxygen; gas_leak", has_1g_comparison="",
    key_findings="Inverse flames reached oxidizer O2 mole fractions up to 85% (highest O2 among PSI microgravity tests).",
    notes="Prevention role is a team judgement (O2-enriched data); NASA lists it under gaseous flames."),
}

flex_m, flex_h = F["FLEX_Methanol"], F["FLEX_Heptane"]
ends = flex_m["end"] + flex_h["end"]
INV["PSI-69"]["key_findings"] = (
    f"Of {flex_m['n'] + flex_h['n']} tests, {ends['Extinction']} ended in flame extinction, "
    f"{ends['Completion']} burned to completion and {ends['Disruption']} disrupted (team count from table).")

# --------------------------------------------------------------- configuration rows
B = "table"   # numbers taken from the PSI experimental table
R = "record"  # numbers stated in the PSI record text
N = "not_reported"


def cfg(cid, inv, label, **kw):
    row = dict(config_id=cid, psi_accession=inv, config_label=label)
    row.update(kw)
    return row


CONFIGS = [
 cfg("ACME-FLAME-DESIGN-C01", "PSI-10", "Normal spherical diffusion flames (fuel from burner)",
     fuel_phase="gas", fuel_material=", ".join(F["FD_normal"]["fuels"]) + " (N2-diluted)", fuel_class="gaseous_hydrocarbon",
     sooting_tendency="medium", sample_geometry="spherical_burner", flame_type="diffusion",
     flow_config="radial", o2_min_pct=fl("FD_normal", "o2", 0), o2_max_pct=fl("FD_normal", "o2", 1), o2_reference="ambient",
     pressure_min_kpa=fl("FD_normal", "p", 0), pressure_max_kpa=fl("FD_normal", "p", 1), diluent="N2",
     atmosphere_basis=B, gravity_level="microgravity",
     measured_outputs="video; flame_temperature; soot_volume_fraction; radiant_flux; extinction_condition",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss",
     key_findings="", test_count_config=F["FD_normal"]["n"],
     tests_table_ref="PSI-10_Experimental table_Flame Design_Normal Flame.csv"),
 cfg("ACME-FLAME-DESIGN-C02", "PSI-10", "Inverse spherical diffusion flames (oxidizer from burner into ethylene/N2)",
     fuel_phase="gas", fuel_material=f"ethylene ambient ({fl('FD_inverse','xf',0)}–{fl('FD_inverse','xf',1)}% in N2)", fuel_class="gaseous_hydrocarbon",
     sooting_tendency="medium", sample_geometry="spherical_burner", flame_type="diffusion",
     flow_config="radial", o2_min_pct=fl("FD_inverse", "o2", 0), o2_max_pct=fl("FD_inverse", "o2", 1), o2_reference="oxidizer_stream",
     pressure_min_kpa=fl("FD_inverse", "p", 0), pressure_max_kpa=fl("FD_inverse", "p", 1), diluent="N2",
     atmosphere_basis=B, gravity_level="microgravity",
     measured_outputs="video; flame_temperature; soot_volume_fraction; radiant_flux; extinction_condition",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss",
     test_count_config=F["FD_inverse"]["n"], tests_table_ref="PSI-10_Experimental table_Flame Design_Inverse Flame.csv"),
 cfg("ACME-BRE-C01", "PSI-20", "Porous gas burner emulating a burning solid, quiescent ambient",
     fuel_phase="gas", fuel_material="methane; ethylene (100% or 50% in N2)", fuel_class="gaseous_hydrocarbon", surrogate_for="solid",
     sooting_tendency="medium", sample_geometry="porous_burner", thickness_mm="25; 50 (burner diameter)", flame_type="diffusion",
     flow_config="quiescent", flow_min_cms=0, flow_max_cms=0, o2_min_pct=21, o2_max_pct=40, o2_reference="ambient",
     pressure_min_kpa=56.5, pressure_max_kpa=101.3, diluent="N2",
     atmosphere_basis="table (O2); record (pressure: 8.2–14.7 psia named in objectives)", gravity_level="microgravity",
     measured_outputs="video; burner_surface_temperature; heat_flux; extinction_condition",
     flammability_boundary_reported="Y", extinction_mechanism="",
     key_findings="Quasi-steady burning without airflow in elevated O2; self-extinction in 21% O2 (record, preliminary).",
     test_count_config=F["BRE"]["flames"], tests_table_ref="PSI-20_Experimental table_ACME BRE.csv",
     source_notes="O2 from the column 'Oxygen Conc (percent)' (lists such as '21; 26.5; 40'). Rows 6 and 9 write '3400%' and '2100%', which cannot be oxygen percentages and are not read; the range 21 to 40% does not depend on them. Pressure 8.2 to 14.7 psia is the set of atmospheres named in the record's objective; the table note says chamber pressures 'are not identified in this summary table'. Test count: the sum of 'Flames Ignited' (flames, not tests). Classification columns are team judgement."),
 cfg("ACME-CLD-C01", "PSI-21", "Coflow laminar diffusion flames, methane and ethylene diluted with N2",
     fuel_phase="gas", fuel_material="methane; ethylene (25–100% in N2)", fuel_class="gaseous_hydrocarbon",
     sooting_tendency="medium", sample_geometry="jet_burner", flame_type="diffusion",
     flow_config="coflow", diluent="N2", atmosphere_basis=N, gravity_level="microgravity",
     measured_outputs="video; flame_temperature; soot_volume_fraction; chemiluminescence; extinction_condition",
     flammability_boundary_reported="Y", test_count_config=F["CLD"]["flames"],
     tests_table_ref="PSI-21_Experimental table_CLD Flame.csv"),
 cfg("ACME-E-FIELD-C01", "PSI-22", "Gas-jet and coflow diffusion flames under an electric field (up to 10 kV)",
     fuel_phase="gas", fuel_material="methane; ethylene (25–100% in N2)", fuel_class="gaseous_hydrocarbon",
     sooting_tendency="medium", sample_geometry="jet_burner", flame_type="diffusion",
     flow_config="quiescent; coflow", diluent="N2", atmosphere_basis=N, gravity_level="microgravity",
     measured_outputs="video; ion_current; soot_volume_fraction",
     flammability_boundary_reported="N", test_count_config=F["EFIELD"]["flames"],
     tests_table_ref="PSI-22_Experimental table_ACME E-FIELD Flames.csv"),
 cfg("ACME-S-FLAME-C01", "PSI-23", "Spherical diffusion flames of H2/CH4/C2H4 with N2 or He",
     fuel_phase="gas", fuel_material="hydrogen; methane; ethylene (diluted with N2 or He)", fuel_class="gaseous_hydrocarbon; hydrogen",
     sooting_tendency="low", sample_geometry="spherical_burner", flame_type="diffusion",
     flow_config="radial", o2_min_pct=21, o2_max_pct=30, o2_reference="ambient", pressure_min_kpa=101.3, pressure_max_kpa=101.3,
     diluent="N2; He", atmosphere_basis="table (approx. ~21% or ~30% O2, ~1 atm)", gravity_level="microgravity",
     measured_outputs="video; flame_temperature; radiant_flux; extinction_condition",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss; blowoff (targeted in objectives)",
     test_count_config=F["SFLAME"]["flames"], tests_table_ref="PSI-23_Experimental table_ACME s-Flame.csv"),
 # ---- BASS-II (PSI-25)
 cfg("BASS-II-C01", "PSI-25", "Thin PMMA films (0.1–0.4 mm), opposed-flow flame spread",
     fuel_phase="solid", fuel_material="PMMA", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="flat_sheet", thickness_mm="0.1–0.4", width_mm="10–20", thermal_regime="thin", flame_type="diffusion",
     flow_config="opposed", flow_min_cms=fl("B2_film", "air", 0), flow_max_cms=fl("B2_film", "air", 1),
     o2_min_pct=fl("B2_film", "o2", 0), o2_max_pct=fl("B2_film", "o2", 1), o2_reference="ambient", diluent="N2",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition; gas_species; radiant_flux",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss",
     key_findings="Linked paper: critical flow velocity for radiative extinction in opposed-flow spread.",
     test_count_config=F["B2_film"]["n"], tests_table_ref="PSI-25_Experimental table_BASS-II.csv (Bhattacharjee films)"),
 cfg("BASS-II-C02", "PSI-25", "PMMA slabs (1–5 mm, one- or two-sided)",
     fuel_phase="solid", fuel_material="PMMA", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="flat_sheet", thickness_mm="1–5", width_mm="10–20", thermal_regime="intermediate; thick", flame_type="diffusion",
     flow_config="opposed; concurrent", flow_min_cms=fl("B2_slab", "air", 0), flow_max_cms=fl("B2_slab", "air", 1),
     o2_min_pct=fl("B2_slab", "o2", 0), o2_max_pct=fl("B2_slab", "o2", 1), o2_reference="ambient", diluent="N2",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition; gas_species; radiant_flux",
     flammability_boundary_reported="Y", test_count_config=F["B2_slab"]["n"],
     tests_table_ref="PSI-25_Experimental table_BASS-II.csv (Miller slabs)"),
 cfg("BASS-II-C03", "PSI-25", "PMMA rods (1/4 to 1/2 inch), axial stagnation flow",
     fuel_phase="solid", fuel_material="PMMA (clear and black)", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="rod", thickness_mm="6.35–12.7 (diameter)", thermal_regime="thick", flame_type="diffusion",
     flow_config="opposed", flow_min_cms=fl("B2_rod", "air", 0), flow_max_cms=fl("B2_rod", "air", 1),
     o2_min_pct=fl("B2_rod", "o2", 0), o2_max_pct=fl("B2_rod", "o2", 1), o2_reference="ambient", diluent="N2",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition; gas_species; radiant_flux",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss; blowoff",
     key_findings="Linked paper: microgravity flammability boundary for PMMA rods in axial stagnation flow (the 'Goldilocks' zone cited by PSI-62).",
     test_count_config=F["B2_rod"]["n"], tests_table_ref="PSI-25_Experimental table_BASS-II.csv (Olson, Fernandez-Pello rods)",
     source_notes="Flow: 'Air display' column (cm/s per the PSI-25 ReadMe), numbers outside brackets; bracketed numbers and numbers after 'pot' are fan or potentiometer readings. "
                  "Numbers above 40 are left out: the PSI-25 record gives 40 cm/s as the tunnel's limit, and rows 53, 54 and 63 carry fan readings (40.5 to 62) in the air column. "
                  "Highest air value 38.5 (row 72, 'incr to max 38.5', flow restrictor out), then 28 (row 73) and 26.5 (row 74). "
                  "The pipeline's flow_cms is each cell's starting flow (highest 20, row 48), so its range is narrower. Classification columns are team judgement."),
 cfg("BASS-II-C04", "PSI-25", "SIBAL cotton-fiberglass fabric strips (1–2 cm wide)",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", width_mm="10–20", thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_min_cms=fl("B2_sibal", "air", 0), flow_max_cms=fl("B2_sibal", "air", 1),
     o2_min_pct=fl("B2_sibal", "o2", 0), o2_max_pct=fl("B2_sibal", "o2", 1), o2_reference="ambient", diluent="N2",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition; gas_species; radiant_flux",
     flammability_boundary_reported="Y", test_count_config=F["B2_sibal"]["n"],
     tests_table_ref="PSI-25_Experimental table_BASS-II.csv (T'ien SIBAL)",
     source_notes="Flow: 'Air display' column read as for BASS-II-C03. Highest air value 29 (row 115, '9 29'). "
                  "Rows 117 ('6 53') and 121 ('11 max(47)') hold numbers above the record's 40 cm/s limit and are not read as air speed: "
                  "47 is in brackets, which the table uses for fan readings, and 53 is the size of the fan reading of row 121 (52). Lowest 1 cm/s; row 107 also records '<1'. "
                  "The pipeline's flow_cms is each cell's starting flow (5 to 11). Classification columns are team judgement."),
 cfg("BASS-II-C05", "PSI-25", "Nomex III fabric",
     fuel_phase="solid", fuel_material="Nomex III", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_min_cms=fl("B2_nomex", "air", 0), flow_max_cms=fl("B2_nomex", "air", 1),
     o2_min_pct=fl("B2_nomex", "o2", 0), o2_max_pct=fl("B2_nomex", "o2", 1), o2_reference="ambient", diluent="N2",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition; gas_species",
     flammability_boundary_reported="Y", test_count_config=F["B2_nomex"]["n"],
     tests_table_ref="PSI-25_Experimental table_BASS-II.csv (Ferkul Nomex)"),
 cfg("BASS-II-C06", "PSI-25", "PMMA spherical section and wax candle (few tests)",
     fuel_phase="solid", fuel_material="PMMA; Japan wax", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="sphere", thermal_regime="thick", flame_type="diffusion",
     flow_config="opposed; concurrent", flow_min_cms=fl("B2_other", "air", 0), flow_max_cms=fl("B2_other", "air", 1),
     o2_min_pct=fl("B2_other", "o2", 0), o2_max_pct=fl("B2_other", "o2", 1), o2_reference="ambient", diluent="N2",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; gas_species", flammability_boundary_reported="N",
     test_count_config=F["B2_other"]["n"], tests_table_ref="PSI-25_Experimental table_BASS-II.csv (spherical section, candle)"),
 # ---- BASS (PSI-26): no flow/O2 columns in the table
 cfg("BASS-C01", "PSI-26", "SIBAL fabric (1–2 cm), concurrent and opposed flow",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", width_mm="10–20", thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_max_cms=40, diluent="N2",
     atmosphere_basis="record (flow up to 40 cm/s); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition", flammability_boundary_reported="N",
     test_count_config=F["B1_sibal"]["n"], tests_table_ref="PSI-26_Experimental table_BASS.csv"),
 cfg("BASS-C02", "PSI-26", "PMMA flat slabs (1–2 cm wide)",
     fuel_phase="solid", fuel_material="PMMA", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="flat_sheet", width_mm="10–20", thermal_regime="thick", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_max_cms=40, diluent="N2",
     atmosphere_basis="record (flow up to 40 cm/s); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition", flammability_boundary_reported="N",
     test_count_config=F["B1_slab"]["n"], tests_table_ref="PSI-26_Experimental table_BASS.csv"),
 cfg("BASS-C03", "PSI-26", "PMMA spheres (1–2 cm), including wake-ignited",
     fuel_phase="solid", fuel_material="PMMA", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="sphere", thickness_mm="10–20 (diameter)", thermal_regime="thick", flame_type="diffusion",
     flow_config="opposed", flow_max_cms=40, diluent="N2",
     atmosphere_basis="record (flow up to 40 cm/s); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition", flammability_boundary_reported="N",
     test_count_config=F["B1_sphere"]["n"], tests_table_ref="PSI-26_Experimental table_BASS.csv"),
 cfg("BASS-C04", "PSI-26", "Wax candles and slabs (Japan wax, paraffin), wake flames",
     fuel_phase="solid", fuel_material="paraffin wax; Japan wax", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="rod; flat_sheet", thermal_regime="thick", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_max_cms=40, diluent="N2",
     atmosphere_basis="record (flow up to 40 cm/s); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; extinction_condition", flammability_boundary_reported="N",
     test_count_config=F["B1_wax"]["n"], tests_table_ref="PSI-26_Experimental table_BASS.csv"),
 cfg("BASS-C05", "PSI-26", "Nomex and Ultem sheets",
     fuel_phase="solid", fuel_material="Nomex III; Ultem", fuel_class="fabric; thermoplastic_solid", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_max_cms=40, diluent="N2",
     atmosphere_basis="record (flow up to 40 cm/s); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; extinction_condition", flammability_boundary_reported="N",
     test_count_config=F["B1_sheet"]["n"], tests_table_ref="PSI-26_Experimental table_BASS.csv"),
 cfg("CFI-C01", "PSI-39", "n-dodecane and n-dodecane/iso-dodecane droplets, cool flames",
     fuel_phase="liquid", fuel_material="n-dodecane; n-dodecane/iso-dodecane (75/25, 60/40)", fuel_class="liquid_hydrocarbon",
     sooting_tendency="medium", sample_geometry="droplet", flame_type="cool_flame; diffusion",
     flow_config="quiescent", flow_min_cms=0, flow_max_cms=0,
     o2_min_pct=fl("CFI", "o2", 0), o2_max_pct=fl("CFI", "o2", 1), o2_reference="ambient",
     pressure_min_kpa=fl("CFI", "p", 0), pressure_max_kpa=fl("CFI", "p", 1), diluent="N2; He",
     diluent_max_pct=fl("CFI", "he", 1), atmosphere_basis=B, gravity_level="microgravity", ignition_method="hot_wire",
     measured_outputs="video; burning_rate; extinction_condition; chemiluminescence; radiant_flux",
     flammability_boundary_reported="Y", test_count_config=F["CFI"]["n"],
     tests_table_ref="PSI-39_Experimental table_CFI.csv",
     source_notes=f"Test count: {F['CFI']['n'] + F['CFI']['dup']} table rows less {F['CFI']['dup']} that repeat rows 24 to 31 cell for cell (rows 81 to 88: same Flex number, date, time and CIR id). "
                  "Values from the PSI table as stated in atmosphere_basis; classification columns are team judgement."),
 cfg("DAFT-C01", "PSI-47", "Aerosol standard (Arizona Road Dust) counted by modified P-Trak and DustTrak",
     fuel_phase="aerosol", fuel_material="Arizona Road Dust (fine)", fuel_class="particulate", flame_type="none",
     flow_config="", atmosphere_basis=N, gravity_level="microgravity",
     measured_outputs="particle_count", flammability_boundary_reported="N", test_count_config=2,
     tests_table_ref="PSI-47_Experimental table_DAFT.csv"),
 cfg("SPICE-ANALYSIS-C01", "PSI-60", "Re-analysis of SPICE jet flames (soot temperature and volume fraction) with soot modelling",
     fuel_phase="gas", fuel_material="SPICE fuels (ethylene and others)", fuel_class="gaseous_hydrocarbon", sooting_tendency="high",
     sample_geometry="jet_burner", flame_type="diffusion", flow_config="coflow", atmosphere_basis=N,
     gravity_level="microgravity; 1g (simulated)", measured_outputs="soot_volume_fraction; flame_temperature (derived)",
     flammability_boundary_reported="N", test_count_config="", tests_table_ref=""),
 cfg("BASS-FGM-MODEL-C01", "PSI-62", "Model of concurrent flame spread over PMMA sheets, spheres, rods and wax cylinders",
     fuel_phase="solid", fuel_material="PMMA; wax", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="flat_sheet; sphere; rod", thermal_regime="thin; thick", flame_type="diffusion",
     flow_config="concurrent", atmosphere_basis=N, gravity_level="microgravity (model)",
     measured_outputs="flame_temperature; soot_volume_fraction; flame_spread_rate (derived)",
     flammability_boundary_reported="Y", test_count_config="", tests_table_ref=""),
 cfg("FLEX-2-C01", "PSI-68", "Alkane and bi-component droplets (iso-octane, n-octane, heptane, decane, heptane/iso-octane)",
     fuel_phase="liquid", fuel_material="iso-octane; n-octane; n-heptane; n-decane; heptane/iso-octane 50/50", fuel_class="liquid_hydrocarbon",
     sooting_tendency="medium", sample_geometry="droplet", thickness_mm="1.5–5 (initial diameter)", flame_type="diffusion",
     flow_config="quiescent", flow_min_cms=0.1, flow_max_cms=5, o2_min_pct=17, o2_max_pct=30, o2_reference="ambient",
     pressure_min_kpa=round(0.5 * ATM_KPA, 1), pressure_max_kpa=round(3.0 * ATM_KPA, 1), diluent="N2; He",
     atmosphere_basis="table (test matrix ranges)", gravity_level="microgravity",
     measured_outputs="video; burning_rate; extinction_condition; soot_volume_fraction",
     flammability_boundary_reported="Y", test_count_config="", tests_table_ref="PSI-68_Experimental table_Flex2.csv"),
 cfg("FLEX-2-C02", "PSI-68", "Alcohol droplets (ethanol; propanol 95% with glycerol 5%; propanol 80% with glycerol 20%)",
     fuel_phase="liquid", fuel_material="ethanol; propanol/glycerol", fuel_class="liquid_alcohol",
     sooting_tendency="low", sample_geometry="droplet", thickness_mm="1.5–5 (initial diameter)", flame_type="diffusion",
     flow_config="quiescent", flow_min_cms=0.1, flow_max_cms=5, o2_min_pct=17, o2_max_pct=30, o2_reference="ambient",
     pressure_min_kpa=round(0.5 * ATM_KPA, 1), pressure_max_kpa=round(3.0 * ATM_KPA, 1), diluent="N2; He",
     atmosphere_basis="table (test matrix ranges)", gravity_level="microgravity",
     measured_outputs="video; burning_rate; extinction_condition",
     flammability_boundary_reported="Y", test_count_config="", tests_table_ref="PSI-68_Experimental table_Flex2.csv"),
 cfg("FLEX-C01", "PSI-69", "Methanol droplets in O2/N2/CO2/He",
     fuel_phase="liquid", fuel_material="methanol", fuel_class="liquid_alcohol", sooting_tendency="low",
     sample_geometry="droplet", thickness_mm=f"{flex_m['d0'][0]}–{flex_m['d0'][1]} (initial diameter)", flame_type="diffusion",
     flow_config="quiescent", flow_min_cms=0, flow_max_cms=0, o2_min_pct=flex_m["o2"][0], o2_max_pct=flex_m["o2"][1], o2_reference="ambient",
     pressure_min_kpa=flex_m["p"][0], pressure_max_kpa=flex_m["p"][1], diluent="N2; CO2; He",
     diluent_max_pct=max(flex_m["co2"][1], flex_m["he"][1]), atmosphere_basis=B, gravity_level="microgravity",
     measured_outputs="video; burning_rate; extinction_condition; radiant_flux",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss; dilution",
     key_findings=f"{flex_m['end']['Extinction']} of {flex_m['n']} methanol tests ended in extinction (team count).",
     test_count_config=flex_m["n"], tests_table_ref="PSI-69_Experimental table_FLEX.csv (Fuel = Methanol)"),
 cfg("FLEX-C02", "PSI-69", "n-Heptane droplets in O2/N2/CO2/He",
     fuel_phase="liquid", fuel_material="n-heptane", fuel_class="liquid_hydrocarbon", sooting_tendency="medium",
     sample_geometry="droplet", thickness_mm=f"{flex_h['d0'][0]}–{flex_h['d0'][1]} (initial diameter)", flame_type="diffusion; cool_flame",
     flow_config="quiescent", flow_min_cms=0, flow_max_cms=0, o2_min_pct=flex_h["o2"][0], o2_max_pct=flex_h["o2"][1], o2_reference="ambient",
     pressure_min_kpa=flex_h["p"][0], pressure_max_kpa=flex_h["p"][1], diluent="N2; CO2; He",
     diluent_max_pct=max(flex_h["co2"][1], flex_h["he"][1]), atmosphere_basis=B, gravity_level="microgravity",
     measured_outputs="video; burning_rate; extinction_condition; radiant_flux",
     flammability_boundary_reported="Y", extinction_mechanism="radiative_loss; dilution",
     key_findings=f"{flex_h['end']['Extinction']} of {flex_h['n']} heptane tests ended in extinction (team count).",
     test_count_config=flex_h["n"], tests_table_ref="PSI-69_Experimental table_FLEX.csv (Fuel = Heptane)"),
 cfg("SAFFIRE-I-C01", "PSI-98", "Large SIBAL fabric (0.94 x 0.4 m), concurrent flow 20 cm/s",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", length_mm=940, width_mm=406, thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent", flow_min_cms=20, flow_max_cms=20, o2_min_pct=21.5, o2_max_pct=21.7, o2_reference="ambient",
     atmosphere_basis="table (O2, flow); pressure not reported", gravity_level="microgravity", ignition_method="hot_wire (182 W, 8 s)",
     measured_outputs="video; flame_spread_rate; flame_temperature; radiant_flux; gas_species",
     flammability_boundary_reported="N", extinction_mechanism="burnout",
     key_findings="Burn time 420 s (table).", test_count_config=1, tests_table_ref="PSI-98_Experimental table_SAFFIRE-1.csv (S1)"),
 cfg("SAFFIRE-I-C02", "PSI-98", "Large SIBAL fabric (0.94 x 0.4 m), opposed flow 20 cm/s",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", length_mm=940, width_mm=406, thermal_regime="thin", flame_type="diffusion",
     flow_config="opposed", flow_min_cms=20, flow_max_cms=20, o2_min_pct=21.5, o2_max_pct=21.5, o2_reference="ambient",
     atmosphere_basis="table (O2 approx., flow); pressure not reported", gravity_level="microgravity", ignition_method="hot_wire (182 W, 8 s)",
     measured_outputs="video; flame_spread_rate; flame_temperature; radiant_flux; gas_species",
     flammability_boundary_reported="N", key_findings="Burn time 70 s (table).",
     test_count_config=1, tests_table_ref="PSI-98_Experimental table_SAFFIRE-1.csv (S2)"),
 cfg("SAFFIRE-II-C01", "PSI-99", "Silicone sheets (0.27–1.03 mm), concurrent and opposed 20 cm/s",
     fuel_phase="solid", fuel_material="silicone", fuel_class="charring_solid", melt_behavior="neither", sooting_tendency="low",
     sample_geometry="flat_sheet", thickness_mm="0.27–1.03", length_mm=290, width_mm=50, thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent; opposed", flow_min_cms=20, flow_max_cms=20, o2_min_pct=21.5, o2_max_pct=22.1, o2_reference="ambient",
     atmosphere_basis="table (O2 from CO2 production, flow); pressure not reported", gravity_level="microgravity", ignition_method="hot_wire (80 W, 9.2 s)",
     measured_outputs="video; flame_spread_rate; gas_species", flammability_boundary_reported="Y", extinction_mechanism="",
     key_findings="No sustained burning in microgravity (burn length ~0) for all four silicone samples; in 1g, two burned fully and one burned 7.6 cm (table).",
     test_count_config=4, tests_table_ref="PSI-99_Experimental table_SAFFIRE-2.csv (2-1 to 2-4)"),
 cfg("SAFFIRE-II-C02", "PSI-99", "SIBAL fabric (0.37 mm), concurrent 20 cm/s",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", thickness_mm=0.37, length_mm=290, width_mm=50, thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent", flow_min_cms=20, flow_max_cms=20, o2_min_pct=22.1, o2_max_pct=22.1, o2_reference="ambient",
     atmosphere_basis="table (O2 from CO2 production, flow); pressure not reported", gravity_level="microgravity", ignition_method="hot_wire (80 W, 9.2 s)",
     measured_outputs="video; flame_spread_rate; gas_species", flammability_boundary_reported="N", extinction_mechanism="burnout",
     key_findings="Concurrent spread 2.1–2.6 mm/s over the full 29 cm in microgravity; in 1g the spread was acceleratory (table).",
     test_count_config=2, tests_table_ref="PSI-99_Experimental table_SAFFIRE-2.csv (2-5, 2-6)"),
 cfg("SAFFIRE-II-C03", "PSI-99", "PMMA (thick, up to 1 cm) and PMMA/Nomex composite, concurrent 20 cm/s",
     fuel_phase="solid", fuel_material="PMMA; PMMA with Nomex", fuel_class="thermoplastic_solid", melt_behavior="melts", sooting_tendency="medium",
     sample_geometry="flat_sheet", thickness_mm="0.85–10", length_mm=290, width_mm=50, thermal_regime="thick", flame_type="diffusion",
     flow_config="concurrent", flow_min_cms=20, flow_max_cms=20, o2_min_pct=21.9, o2_max_pct=22.1, o2_reference="ambient",
     atmosphere_basis="table (O2 from CO2 production, flow); pressure not reported", gravity_level="microgravity", ignition_method="hot_wire (80–97 W, 9.2–30 s)",
     measured_outputs="video; flame_spread_rate; gas_species", flammability_boundary_reported="N",
     key_findings="Thick PMMA flames stayed anchored at the sample base with slow regression (0.01–0.04 mm/s); in the composite sample the PMMA burned but the Nomex did not ignite (table notes).",
     test_count_config=3, tests_table_ref="PSI-99_Experimental table_SAFFIRE-2.csv (2-7 to 2-9)"),
 cfg("SAFFIRE-III-C01", "PSI-100", "Large SIBAL fabric (94 x 40.6 cm), concurrent flow 30 cm/s",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", length_mm=940, width_mm=406, thermal_regime="thin", flame_type="diffusion",
     flow_config="concurrent", flow_min_cms=30, flow_max_cms=30,
     atmosphere_basis="table (flow); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; flame_temperature; radiant_flux; gas_species",
     flammability_boundary_reported="N", test_count_config=1, tests_table_ref="PSI-100_Experimental table_SAFFIRE-3.csv (S1)"),
 cfg("SAFFIRE-III-C02", "PSI-100", "Large SIBAL fabric (94 x 40.6 cm), opposed flow 30 cm/s",
     fuel_phase="solid", fuel_material="SIBAL (75% cotton, 25% fiberglass)", fuel_class="fabric", melt_behavior="chars", sooting_tendency="medium",
     sample_geometry="flat_sheet", length_mm=940, width_mm=406, thermal_regime="thin", flame_type="diffusion",
     flow_config="opposed", flow_min_cms=30, flow_max_cms=30,
     atmosphere_basis="table (flow); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_spread_rate; flame_temperature; radiant_flux; gas_species",
     flammability_boundary_reported="N", test_count_config=1, tests_table_ref="PSI-100_Experimental table_SAFFIRE-3.csv (S2)"),
 cfg("SAME-R-C01", "PSI-101", "Smoke from overheated Kapton, silicone, lampwick, Teflon and Pyrell foam",
     fuel_phase="solid", fuel_material=", ".join(F["SAMER"]["mats"]), fuel_class="pyrolyzing_solid", sooting_tendency="",
     sample_geometry="heated_sample", flame_type="none (pyrolysis smoke)",
     flow_config="quiescent; concurrent", flow_min_cms=fl("SAMER", "v", 0), flow_max_cms=fl("SAMER", "v", 1),
     atmosphere_basis="table (inlet velocity); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="particle_size; detector_response; aging_time", flammability_boundary_reported="N",
     key_findings=f"Net smoke aging times {fl('SAMER','age',0)}–{fl('SAMER','age',1)} s (table).",
     test_count_config=F["SAMER"]["n"], tests_table_ref="PSI-101_Experimental table_SAME-R.csv"),
 cfg("SAME-C01", "PSI-102", "Smoke from overheated Teflon, Kapton, silicone rubber, lampwick and dibutyl phthalate",
     fuel_phase="solid", fuel_material="Teflon; Kapton; silicone rubber; lampwick; dibutyl phthalate", fuel_class="pyrolyzing_solid",
     sample_geometry="heated_sample", flame_type="none (pyrolysis smoke)",
     flow_config="concurrent", flow_min_cms=5, flow_max_cms=10,
     atmosphere_basis="table (air flow); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="particle_size; detector_response; mass_loss", flammability_boundary_reported="N",
     key_findings="Conditions: 5–10 cm/s, weight-loss rate 1–2 mg/min, aging 1–20 min (table).",
     test_count_config=4, tests_table_ref="PSI-102_Experimental table_SAME.csv",
     source_notes="Test count: rows 2 to 5 (samples 1 to 4, Teflon) record air flow, weight-loss rate and aging time. Rows 6 to 9 (Kapton, silicone rubber, lampwick, dibutyl phthalate) say 'same conditions as 1-4' and record no values, "
                  "so they are not counted as separate tests (the table had been counted as 8). Classification columns are team judgement."),
 cfg("SLICE-C01", "PSI-106", "Coflow jet diffusion flames (methane, ethane, ethylene; N2-diluted)",
     fuel_phase="gas", fuel_material="methane (20–100% in N2); ethylene (20%, 100%); ethane", fuel_class="gaseous_hydrocarbon",
     sooting_tendency="medium", sample_geometry="jet_burner", flame_type="diffusion",
     flow_config="coflow", diluent="N2", atmosphere_basis=N, gravity_level="microgravity",
     measured_outputs="video; flame_temperature; liftoff_height", flammability_boundary_reported="N",
     test_count_config=12, tests_table_ref="PSI-106_Experimental table_Slice.csv (test days)"),
 cfg("SPICE-C01", "PSI-107", "Jet diffusion flames in coflow at the smoke point",
     fuel_phase="gas", fuel_material=", ".join(F["SPICE"]["fuels"]), fuel_class="gaseous_hydrocarbon", sooting_tendency="high",
     sample_geometry="jet_burner", thickness_mm="0.41; 0.76; 1.6 (nozzle diameter)", flame_type="diffusion",
     flow_config="coflow", flow_min_cms=fl("SPICE", "air", 0), flow_max_cms=fl("SPICE", "air", 1),
     atmosphere_basis="table (air rate); O2 and pressure not reported", gravity_level="microgravity",
     measured_outputs="video; flame_length; smoke_point; radiant_flux", flammability_boundary_reported="N",
     test_count_config=F["SPICE"]["n"], tests_table_ref="PSI-107_Experimental table_Spice.csv",
     source_notes=f"Flow: column 'Air Rate (cm/s)' of the {F['SPICE']['n']} distinct rows, {fl('SPICE', 'air', 0):g} to {fl('SPICE', 'air', 1):g} cm/s; "
                  f"{len(F['SPICE']['air_negative'])} negative cells ({', '.join(f'{v:g}' for v in sorted(set(F['SPICE']['air_negative'])))}) are left out as unreadable. The record states coflow 5.4 to 65 cm/s. "
                  f"Test count: {F['SPICE']['n'] + F['SPICE']['dup']} table rows less {F['SPICE']['dup']} that repeat an earlier row cell for cell (for example row 3 = row 2). Classification columns are team judgement."),
 cfg("SAME-SIM-C01", "PSI-115", "DNS of dibutyl phthalate smoke particle growth, 1g vs microgravity",
     fuel_phase="solid", fuel_material="dibutyl phthalate (pyrolysis vapor)", fuel_class="pyrolyzing_solid",
     sample_geometry="heated_sample", flame_type="none (pyrolysis smoke)", flow_config="concurrent",
     atmosphere_basis=N, gravity_level="microgravity; 1g (simulated)", measured_outputs="particle_size (simulated)",
     flammability_boundary_reported="N", test_count_config="", tests_table_ref=""),
 cfg("COOLFLAME-CFD-C01", "PSI-117", "CFD of n-alkane droplet cool flames (0.5–4 mm) with imposed perturbations",
     fuel_phase="liquid", fuel_material="n-alkanes", fuel_class="liquid_hydrocarbon", sample_geometry="droplet",
     thickness_mm="0.5–4 (diameter)", flame_type="cool_flame", flow_config="quiescent", atmosphere_basis=N,
     gravity_level="microgravity (model)", measured_outputs="extinction_condition; ignition_delay (simulated)",
     flammability_boundary_reported="Y", test_count_config="", tests_table_ref=""),
 cfg("COOLFLAME-COUNTERFLOW-C01", "PSI-142", "Ground counterflow cool flames (DME, n-heptane, n-decane, n-dodecane; ozone-assisted)",
     fuel_phase="gas", fuel_material="dimethyl ether; n-heptane; n-decane; n-dodecane", fuel_class="gaseous_hydrocarbon; liquid_hydrocarbon",
     sample_geometry="counterflow_burner", flame_type="cool_flame", flow_config="counterflow", atmosphere_basis=N,
     gravity_level="1g (ground)", measured_outputs="extinction_condition; flame_temperature; gas_species",
     flammability_boundary_reported="Y", test_count_config=8, tests_table_ref="PSI-142_Experimental table_Data Summary Table.csv (figure list)"),
 cfg("ACME-CFI-G-C01", "PSI-159", "Normal spherical cool diffusion flames (ethane, propane, butane)",
     fuel_phase="gas", fuel_material=", ".join(F["CFIG_normal"]["fuels"]), fuel_class="gaseous_hydrocarbon", sooting_tendency="medium",
     sample_geometry="spherical_burner", flame_type="cool_flame; diffusion", flow_config="radial",
     o2_min_pct=fl("CFIG_normal", "o2", 0), o2_max_pct=fl("CFIG_normal", "o2", 1), o2_reference="ambient",
     pressure_min_kpa=fl("CFIG_normal", "p", 0), pressure_max_kpa=fl("CFIG_normal", "p", 1), diluent="N2",
     atmosphere_basis=B, gravity_level="microgravity",
     measured_outputs="video; flame_temperature; burner_surface_temperature; extinction_condition",
     flammability_boundary_reported="Y", test_count_config=F["CFIG_normal"]["n"],
     tests_table_ref="PSI-159_Experimental table_CFI-G_Normal Flames.csv"),
 cfg("ACME-CFI-G-C02", "PSI-159", "Inverse spherical cool diffusion flames (oxidizer up to 85% O2 into ethane/propane/butane)",
     fuel_phase="gas", fuel_material=", ".join(F["CFIG_inverse"]["fuels"]) + " (ambient)", fuel_class="gaseous_hydrocarbon", sooting_tendency="medium",
     sample_geometry="spherical_burner", flame_type="cool_flame; diffusion", flow_config="radial",
     o2_min_pct=fl("CFIG_inverse", "o2", 0), o2_max_pct=fl("CFIG_inverse", "o2", 1), o2_reference="oxidizer_stream",
     pressure_min_kpa=fl("CFIG_inverse", "p", 0), pressure_max_kpa=fl("CFIG_inverse", "p", 1), diluent="N2",
     atmosphere_basis=B, gravity_level="microgravity",
     measured_outputs="video; flame_temperature; burner_surface_temperature; extinction_condition",
     flammability_boundary_reported="Y", test_count_config=F["CFIG_inverse"]["n"],
     tests_table_ref="PSI-159_Experimental table_CFI-G_Inverse Flames.csv"),
]

INV_COLS = ["investigation_id", "psi_accession", "investigation_name", "project_group", "tier", "platform",
            "hardware", "operation_period", "objectives", "research_focus", "fire_safety_role",
            "fire_scenario_tags", "mu_g_duration_class", "has_1g_comparison", "data_availability",
            "test_count", "key_findings", "psi_url", "psi_dataset_id", "dataset_doi", "doi_list",
            "license", "source_notes", "verification_status", "verified_by", "collected_on"]
CFG_COLS = ["config_id", "investigation_id", "psi_accession", "config_label",
            "fuel_phase", "fuel_material", "fuel_class", "melt_behavior", "surrogate_for", "sooting_tendency",
            "sample_geometry", "thickness_mm", "length_mm", "width_mm", "thermal_regime", "flame_type",
            "flow_config", "flow_min_cms", "flow_max_cms",
            "o2_min_pct", "o2_max_pct", "o2_reference", "pressure_min_kpa", "pressure_max_kpa",
            "ppo2_min_kpa", "ppo2_max_kpa", "diluent", "diluent_max_pct", "ambient_temp_k",
            "atmosphere_basis", "o2_source", "pressure_source", "flow_source", "gravity_level", "ignition_method",
            "measured_outputs", "flammability_boundary_reported", "extinction_mechanism", "key_findings",
            "test_count_config", "tests_table_ref", "source_notes", "verification_status"]


# Where each oxygen, pressure and flow number comes from, so the ranking never words a planned
# or read-in value as "tested". Default: "table" when the value is set (a value per test or per
# test group in a PSI experimental table), "" when it is empty. The exceptions:
#   record      named in the PSI record text, not a test value in a table
#   test_matrix a planned test-matrix table (conditions joined by "or"), not individual tests
#   team        a team reading with no number in the table or the record
VALUE_SOURCES = {
    "ACME-BRE-C01": dict(pressure="record", flow="team"),  # objective: "will be examined: 14.7 psia ... 8.2 psia";
                                                             # table note: pressures "not identified in this summary table";
                                                             # 0 cm/s is the team's reading of "quiescent microgravity ambient"
    **{f"BASS-C0{i}": dict(flow="record") for i in range(1, 6)},  # approach: flow "up to 40 cm/s"
    "FLEX-2-C01": dict(o2="test_matrix", pressure="test_matrix", flow="test_matrix"),
    "FLEX-2-C02": dict(o2="test_matrix", pressure="test_matrix", flow="test_matrix"),
    "FLEX-C01": dict(flow="team"), "FLEX-C02": dict(flow="team"),  # droplets read as quiescent; no flow column
    "CFI-C01": dict(flow="team"),
}


def value_sources(r):
    out = {}
    for var, (lo, hi) in (("o2", ("o2_min_pct", "o2_max_pct")), ("pressure", ("pressure_min_kpa", "pressure_max_kpa")),
                          ("flow", ("flow_min_cms", "flow_max_cms"))):
        has = r.get(lo, "") != "" or r.get(hi, "") != ""
        src = VALUE_SOURCES.get(r["config_id"], {}).get(var, "table") if has else ""
        assert not (src and not has), (r["config_id"], var)
        out[f"{var}_source"] = src
    basis = r.get("atmosphere_basis", "")
    assert ("record" in basis) == ("record" in out.values()), (r["config_id"], basis, out)
    assert ("matrix" in basis) == ("test_matrix" in out.values()), (r["config_id"], basis, out)
    return out


def platform_of(d):
    hw = (d.get("experimentHardware") or "").lower()
    if d.get("projectType", "").lower().startswith("ground"):
        return "ground"
    if "cygnus" in hw or "cygnus" in (d.get("flightProgram") or "").lower():
        return "free_flyer (Cygnus)"
    return "ISS"


def table_rows(acc, manifest):
    total = 0
    for t in manifest[acc]["experimental_tables"]:
        _, rows = load_table(t["file"])
        total += len(rows)
    return total


def main():
    os.makedirs(OUT, exist_ok=True)
    man = {i["accession"]: i for i in json.load(open(os.path.join(PSI, "manifest.json")))["investigations"]}
    assert len(man) == 24, len(man)
    count_override = {"PSI-20": F["BRE"]["flames"], "PSI-21": F["CLD"]["flames"],
                      "PSI-22": F["EFIELD"]["flames"], "PSI-23": F["SFLAME"]["flames"]}
    inv_rows, id_of = [], {}
    for acc in sorted(man, key=lambda a: int(a.split("-")[1])):
        d = json.load(open(os.path.join(PSI, "catalog", f"{acc}.json")))
        c = INV[acc]
        id_of[acc] = c["investigation_id"]
        plat = platform_of(d)
        ground = plat == "ground"
        has_table = bool(man[acc]["experimental_tables"])
        if ground:
            avail = "derived_analysis"
        elif acc == "PSI-68":
            avail = "summary_table"
        else:
            avail = "raw_table" if has_table else "papers_only"
        dois = [p.get("doi") for p in d.get("publications", []) if isinstance(p, dict) and p.get("doi")]
        start, end = d.get("investigationStartDate") or "", d.get("investigationEndDate") or ""
        inv_rows.append(dict(
            investigation_id=c["investigation_id"], psi_accession=acc,
            investigation_name=re.sub(r"\s+", " ", d.get("title", "")).strip(),
            project_group=c["project_group"], tier=c["tier"], platform=plat,
            hardware=re.sub(r"\s+", " ", d.get("experimentHardware") or "").strip(),
            operation_period=f"{start} to {end}".strip(" to") if (start or end) else "",
            objectives=c["objectives"], research_focus=c["research_focus"],
            fire_safety_role=c["fire_safety_role"], fire_scenario_tags=c["fire_scenario_tags"],
            mu_g_duration_class="none (ground)" if ground else "long",
            has_1g_comparison=c["has_1g_comparison"], data_availability=avail,
            test_count=count_override.get(acc, table_rows(acc, man) if has_table and acc not in ("PSI-68", "PSI-142") else ""),
            key_findings=c["key_findings"],
            psi_url=f"https://psi.nasa.gov/physci/repo/data/investigations/{acc}",
            psi_dataset_id=acc, dataset_doi=man[acc]["doi"], doi_list="; ".join(dois[:6]),
            license=man[acc].get("license") or "not stated in record",
            source_notes=c["notes"], verification_status="ai_extracted", verified_by="",
            collected_on=COLLECTED_ON))
    cfg_rows = []
    for r in CONFIGS:
        r = dict(r)
        r["investigation_id"] = id_of[r["psi_accession"]]
        o2a, o2b = r.get("o2_min_pct", ""), r.get("o2_max_pct", "")
        pa, pb = r.get("pressure_min_kpa", ""), r.get("pressure_max_kpa", "")
        if r.get("o2_reference") == "ambient" and o2a != "" and pa != "":
            r["ppo2_min_kpa"] = round(o2a / 100 * pa, 1)
            r["ppo2_max_kpa"] = round(o2b / 100 * pb, 1)
        r.update(value_sources(r))
        r.setdefault("verification_status", "ai_extracted")
        r.setdefault("source_notes", "Values from PSI record/table as stated in atmosphere_basis; classification columns are team judgement.")
        cfg_rows.append(r)
    # sanity checks
    ids = [r["config_id"] for r in cfg_rows]
    assert len(ids) == len(set(ids)), "duplicate config_id"
    assert set(r["psi_accession"] for r in cfg_rows) == set(man), "every investigation needs >= 1 configuration"
    for r in cfg_rows:
        for a, b in (("o2_min_pct", "o2_max_pct"), ("pressure_min_kpa", "pressure_max_kpa"), ("flow_min_cms", "flow_max_cms")):
            if r.get(a, "") != "" and r.get(b, "") != "":
                assert float(r[a]) <= float(r[b]), (r["config_id"], a, r[a], r[b])
    for name, cols, rows in (("investigations.csv", INV_COLS, inv_rows), ("configurations.csv", CFG_COLS, cfg_rows)):
        with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="raise")
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k, "") for k in cols})
    print(f"wrote {len(inv_rows)} investigations, {len(cfg_rows)} configurations -> {OUT}")


if __name__ == "__main__":
    main()
