# AI-generated code: written with an AI coding assistant (Claude Code)
# during the NASA Space Apps Challenge 2026 hackathon (2026-11-14).
"""Named cell rules used by pipeline/spec/sources.json.

A rule turns one source cell into one standard value (or, for the two BASS
rules, several). Rules never estimate: a cell that cannot be read by the rule
gives an empty value plus a flag, and the source row number is kept so the
cell can be looked up.

Signature: rule(cell, flags, var, **params) -> value | dict | None
"""
import re

NUM = re.compile(r"^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$")
FIRST_NUM = re.compile(r"\d+(?:\.\d+)?|\.\d+")
EMPTY = {"", "-", "n/a", "na"}
LENGTH_TO_MM = {"mm": 1.0, "cm": 10.0, "micron": 0.001, "in": 25.4}


def _plain(cell):
    return float(cell) if NUM.match(cell or "") else None


def text(cell, flags, var, **_):
    return cell or None


def lower(cell, flags, var, **_):
    return cell.lower() or None


def number(cell, flags, var, factor=1.0, **_):
    """A plain number, optionally multiplied by a unit factor. '~6', '>500',
    'OR' are not plain numbers: empty value and a flag."""
    if cell.lower() in EMPTY:
        return None
    value = _plain(cell)
    if value is None:
        flags.append(f"{var}:not_a_number_in_source")
        return None
    return round(value * factor, 4)


def measure(cell, flags, var, factor=1.0, **_):
    """First number in a cell that may carry a unit, '~' or a note,
    e.g. '20 cm/s', '~ 10 cm (note 3)'. Text without a number gives a flag."""
    if cell.lower() in EMPTY:
        return None
    m = FIRST_NUM.search(cell)
    if not m:
        flags.append(f"{var}:text_in_source")
        return None
    if "~" in cell:
        flags.append(f"{var}:approximate_in_source")
    if "note" in cell.lower() or "&" in cell:
        flags.append(f"{var}:see_note_in_source")
    return round(float(m.group(0)) * factor, 4)


def length(cell, flags, var, default_unit="mm", out="mm", **_):
    """Length with the unit written in the cell, or default_unit if none."""
    value = measure(cell, flags, var)
    if value is None:
        return None
    unit = next((u for u in ("micron", "mm", "cm") if u in cell.lower()), default_unit)
    return round(value * LENGTH_TO_MM[unit] / LENGTH_TO_MM[out], 4)


def o2_text(cell, flags, var, **_):
    """'21.5', '~ 21.5', '21.5 - 21.7', '22.1 to 22.0' -> percent."""
    values = [float(v) for v in FIRST_NUM.findall(cell)]
    if not values:
        return None
    if len(values) >= 2:
        flags.append(f"{var}:range_in_source_midpoint_used")
        return round(sum(values[:2]) / 2, 3)
    if "~" in cell:
        flags.append(f"{var}:approximate_in_source")
    return values[0]


def gas_reading(cell, flags, var, **_):
    """Gas analyser reading. 'OR' = over range (BASS-II ReadMe)."""
    if cell.lower() in ("or", "over"):
        flags.append(f"{var}:over_range_in_source")
        return None
    if cell.startswith(">"):
        flags.append(f"{var}:lower_bound_in_source")
        return None
    return number(cell, flags, var)


def codes(cell, flags, var, map=None, **_):
    """Fixed code list; a code that is not in the list is kept as written."""
    if cell.lower() in EMPTY:
        return None
    return (map or {}).get(cell.lower(), cell.lower())


ROD_INCH = [(r"1/4", 0.25), (r"3/8", 0.375), (r"1/2", 0.5), (r"0\.5\s*\"", 0.5)]


def bass_material(cell, flags, var, **_):
    """BASS / BASS-II 'Fuel Sample Material' -> material, shape, dimensions.
    Keyword rules; the PSI-25 ReadMe states the unlabelled films are PMMA."""
    s = cell.lower()
    out = {}
    width = re.search(r"(\d+(?:\.\d+)?)\s*cm", s)
    width = float(width.group(1)) if width else None
    if "sibal" in s:
        out = {"fuel_material": "SIBAL fabric (75% cotton, 25% fiberglass)",
               "sample_geometry": "fabric sheet", "sample_width_cm": width}
    elif "nomex" in s:
        out = {"fuel_material": "Nomex III fabric", "sample_geometry": "fabric sheet"}
    elif "wax" in s or "candle" in s:
        out = {"fuel_material": "Japan wax", "sample_geometry": "candle"}
    elif "rod" in s:
        out = {"fuel_material": "PMMA", "sample_geometry": "rod"}
        for pattern, inches in ROD_INCH:
            if re.search(pattern, s):
                out["rod_diameter_mm"] = round(inches * 25.4, 3)
                break
    elif "spher" in s:
        out = {"fuel_material": "PMMA", "sample_geometry": "spherical section",
               "sample_width_cm": width}
    else:
        micron = re.search(r"(\d+(?:\.\d+)?)\s*micron", s)
        mm = re.search(r"(\d+(?:\.\d+)?)\s*mm", s)
        thick = float(micron.group(1)) / 1000 if micron else float(mm.group(1)) if mm else None
        if thick is not None:
            out = {"fuel_material": "PMMA", "sample_thickness_mm": round(thick, 4),
                   "sample_geometry": "film" if thick < 1.0 else "slab",
                   "sample_width_cm": width}
        elif "pmma" in s:
            out = {"fuel_material": "PMMA", "sample_width_cm": width,
                   "sample_geometry": "slab" if "slab" in s else None}
        elif "ultem" in s:
            out = {"fuel_material": "Ultem", "sample_geometry": "sheet"}
    if not out.get("fuel_material"):
        flags.append("fuel_material:not_parsed")
    return out


def bass_flow(cell, flags, var, max_cms=40.0, **_):
    """BASS-II 'Air display' = duct flow speed in cm/s (ReadMe). A cell can
    list the settings of one test, e.g. '5  3  2   ext'. Control-box 'pot'
    settings are not speeds. Numbers above the duct maximum are fan-display
    readings written in this column and are not used."""
    s = re.sub(r"pot\s*[\d.]+|[\d.]+\s*pot", " ", cell.lower())
    numbers = [float(n) for n in re.findall(r"(?<![<\d.])\d+(?:\.\d+)?", s)]
    if any(n > max_cms for n in numbers):
        flags.append("flow_cms:fan_reading_in_flow_cell_ignored")
    numbers = [n for n in numbers if n <= max_cms]
    below_1 = "<1" in s.replace(" ", "")
    if cell and not numbers and not below_1:
        flags.append("flow_cms:not_parsed")
    if below_1:
        flags.append("flow_min_cms:below_1_cms_in_source")
    return {
        "flow_cms": numbers[0] if numbers and not s.strip().startswith("<") else None,
        "flow_min_cms": min(numbers) if numbers else None,
        "flow_event": ("blowoff" if "blowoff" in s else "no_ignition" if "no ign" in s
                       else "not_sustained" if "would not stay lit" in s
                       else "extinction" if "ext" in s else None),
    }


RULES = {f.__name__: f for f in (text, lower, number, measure, length, o2_text,
                                 gas_reading, codes, bass_material, bass_flow)}
