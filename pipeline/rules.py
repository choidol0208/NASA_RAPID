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
POINTER = re.compile(r"\(?\b(?:see\s+)?(?:note|fig\.?|figure|table)\s*\d+\)?", re.I)
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
    """The one number in a cell that may carry a unit, '~' or a pointer to a
    note, e.g. '20 cm/s', '~ 10 cm (note 3)'. The number of a pointer
    ('Note 4', 'See Fig. 5') is never read as a value. A cell with no number,
    with several numbers ('0.85 and 0.37 mm') or with a number whose decimal
    point is unclear ('037 mm') gives an empty value and a flag."""
    if cell.lower() in EMPTY:
        return None
    body = POINTER.sub(" ", cell)
    if body != cell:
        flags.append(f"{var}:see_note_in_source")
    numbers = FIRST_NUM.findall(body)
    if not numbers:
        if body.strip(" ()"):
            flags.append(f"{var}:text_in_source")
        return None
    if len(numbers) > 1:
        flags.append(f"{var}:several_values_in_source")
        return None
    if re.fullmatch(r"0\d+", numbers[0]):
        flags.append(f"{var}:decimal_point_unclear_in_source")
        return None
    if "~" in cell:
        flags.append(f"{var}:approximate_in_source")
    return round(float(numbers[0]) * factor, 4)


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


NOT_IN_CELL = "fuel_material:not_written_in_cell_named_in_readme"


def sample_keywords(cell, flags, var, entries=(), shape_words=None, rod_inches=None,
                    thickness=None, **_):
    """A free-text sample cell (BASS, BASS-II 'Fuel Sample Material') ->
    material, shape, dimensions. Everything specific is in the params
    (sources.json): 'entries' is an ordered list; the first entry whose
    words are all in the cell gives the material and the shape. A cell that
    gives a thickness and matches no earlier entry follows 'thickness'
    (material, and film or slab by the stated limit). Where the material
    comes from an entry marked 'not_in_cell', or from 'thickness' without
    the material being written, the test is flagged."""
    s = cell.lower()
    width = re.search(r"(\d+(?:\.\d+)?)\s*cm", s)
    width = float(width.group(1)) if width else None
    shape = next((v for k, v in (shape_words or {}).items() if k in s), None)

    def from_entry(e):
        out = {"fuel_material": e["fuel_material"],
               "sample_geometry": e.get("sample_geometry") or shape}
        if e.get("width_from_cell"):
            out["sample_width_cm"] = width
        if e.get("rod"):
            for pattern, inches in (rod_inches or {}).items():
                if re.search(pattern, s):
                    out["rod_diameter_mm"] = round(inches * 25.4, 3)
                    break
        if e.get("not_in_cell"):
            flags.append(NOT_IN_CELL)
        return out

    def first(after):
        return next((e for e in entries if bool(e.get("after_thickness")) == after
                     and all(w in s for w in e["words"])), None)

    entry = first(False)
    if entry:
        return from_entry(entry)
    micron = re.search(r"(\d+(?:\.\d+)?)\s*micron", s)
    mm = re.search(r"(\d+(?:\.\d+)?)\s*mm", s)
    thick = float(micron.group(1)) / 1000 if micron else float(mm.group(1)) if mm else None
    if thick is not None and thickness:
        if thickness["fuel_material"].lower() not in s:
            flags.append(NOT_IN_CELL)
        return {"fuel_material": thickness["fuel_material"], "sample_thickness_mm": round(thick, 4),
                "sample_geometry": thickness["below"] if thick < thickness["limit_mm"] else thickness["from"],
                "sample_width_cm": width}
    entry = first(True)
    if entry:
        return from_entry(entry)
    flags.append("fuel_material:not_parsed")
    return {}


def _event(s):
    return ("blowoff" if "blowoff" in s else "no_ignition" if "no ign" in s
            else "not_sustained" if "would not stay lit" in s
            else "extinction" if re.search(r"\bext|\dext", s) else None)


def bass_flow(cell, flags, var, max_cms=40.0, **_):
    """BASS-II 'Air display' = duct flow speed in cm/s (ReadMe). A cell can
    list the settings of one test, e.g. '5  3  2   ext', and can also hold
    fan potentiometer settings and fan-display readings, which are not
    speeds. Only what is unambiguous is read:
      flow_cms      the number the cell starts with;
      flow_min_cms  the lowest number listed, and only if the cell has no
                    potentiometer settings ('pot') and no brackets;
      flow_event    the event word in the cell.
    Numbers in brackets are never read. Numbers above the duct maximum are
    fan-display readings and are not used."""
    s = cell.lower()
    if not s:
        return {}
    outside = re.sub(r"\([^)]*\)?", " ", s)
    has_pot = "pot" in s
    bracketed = "(" in s
    numbers = [float(n) for n in re.findall(r"(?<![<\d.])\d+(?:\.\d+)?|(?<![<\d.])\.\d+", outside)]
    if any(n > max_cms for n in numbers):
        flags.append("flow_cms:fan_reading_in_flow_cell_ignored")
    first = re.match(r"~?\s*(\d+(?:\.\d+)?)(?!\s*pot\b)", outside.strip())
    start = float(first.group(1)) if first and float(first.group(1)) <= max_cms else None
    below_1 = "<1" in s.replace(" ", "")
    if start is None and not below_1:
        flags.append("flow_cms:not_parsed")
    if below_1:
        flags.append("flow_min_cms:below_1_cms_in_source")
    lowest = None
    if has_pot or bracketed:
        flags.append("flow_min_cms:potentiometer_or_bracketed_values_in_cell_not_read")
    else:
        usable = [n for n in numbers if n <= max_cms]
        lowest = min(usable) if usable else None
        if lowest is not None and re.search(r"down|decr|low|etc", s):
            flags.append("flow_min_cms:cell_says_flow_went_lower_than_written")
    return {"flow_cms": start, "flow_min_cms": lowest, "flow_event": _event(s)}


def event_words(cell, flags, var, **_):
    """An event word in a free-text cell (BASS-II 'Fan display'): 'ext',
    'extinguished', 'blowoff', 'no ign', 'would not stay lit'."""
    return _event(cell.lower())


RULES = {f.__name__: f for f in (text, lower, number, measure, length, o2_text,
                                 gas_reading, codes, sample_keywords, bass_flow,
                                 event_words)}
