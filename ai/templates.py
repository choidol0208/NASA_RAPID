# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Fixed wording for the baseline product files (ai/build_baseline.py).

Every sentence shown to users in data/insights/scenarios.json and cards.json
comes from a template in this file, filled by code with counts computed from the
pipeline CSVs or with text copied from a NASA source. No language model writes
any of it.

Wording rules (coord/decisions.md 11:20 and 12:15; docs/ai_layer_design.json A2):
- counts are recorded tests in the team's bins, never a statement about how a
  material behaves, a prediction, a safe/unsafe verdict or advice;
- 'not a column in the PSI table' where that is the fact, never 'not tested' and
  never a filled-in value (an empty cell is never 0 and never 101 kPa);
- oxidizer-stream oxygen is never matched to a cabin atmosphere;
- microgravity and 1 g results are never offered as bounds for lunar or Martian
  gravity;
- a need whose status is in_atmosphere is never worded as 'covered'.

Wording review of 14 November (a second AI session read every statement against the pipeline CSVs,
the NASA tables and pipeline/spec/references.json). What changed and why is in the comments marked
'review:' below; the main ones:
- a NASA cell that holds a value the pipeline does not use (FLEX test 114: pressure '0' mmHg, flag
  out_of_range) is no longer called an empty cell;
- 'not bounds for lunar gravity' is no longer stated as the team's own scientific finding without a
  source: the page says it does not treat the results as bounds, and cites what NASA documents say;
- tests recorded outside the stated objective are said to include burner-stream (inverse-flame)
  tests where they do;
- the PSI-20 oxygen values are called what its table calls them (approximate concentrations for
  the tests that ignited), not settings;
- no rank word ('the first two'), and no 'recommends', even in an attribution.

Careful-reader pass (14 November, afternoon; an AI session of the pm role read every sentence for iss and
lunar_habitat as a combustion scientist would and recounted the numbers from tests.csv). Changes are marked
'reader:' below; the main ones:
- lunar habitat (coord/decisions.md 14:15): wherever the 17 matched droplet tests are counted, the text says
  the pressure they were recorded at and that it is above the 10.2 psi of the challenge statement, and the
  frame says that no counted test was recorded at 30% oxygen or more and at or below 10.2 psi;
- 'Droplet disruption is not flame extinction' stated a physical meaning for a word the FLEX table does not
  define; the note now says only that 'disruption' and 'extinction' are separate values of the column;
- the Olson and Ferkul sentence no longer calls the tests 'NASA drop-tower tests' (the reference item does
  not say whose drop tower), says how many materials the table has and what a limiting oxygen
  concentration is;
- '126 further tests' after 'no test is counted', 'usable for' beside 'counted for', and two spellings of
  the same table (SAFFIRE-II, SAFFIRE-2) are gone; the flow comparison says where the remaining tests are.

Pipeline sentences (14 November, after the data role's audit): where data/pipeline/evidence/scenario_<id>.json
has a fixed sentence that says the same thing as a team sentence (the status of a need, the need's reading,
the oxygen, pressure, flow and gravity gaps, the flow comparison), the build uses the pipeline's sentence as
written and cites it as data/pipeline/evidence/scenario_<id>.json#<need id>/<statement id>; the templates
below are kept for what the pipeline does not say (which table lacks a column, balance gas, test ends,
the investigations outside the stated objective).
"""

BUILT_BY = "ai/build_baseline.py"

SCENARIO_MODEL = "none: counts and fixed sentences filled by team code"
CARD_MODEL = "none: verbatim NASA text chosen by team code"

SCENARIO_LABEL = (
    "Computed by the team's code from NASA PSI tables (code written with an AI assistant). "
    "Counts of recorded tests in the team's bins; not a statement about how a material behaves; "
    "not NASA's conclusion; not operational safety guidance.")
# review: the label names the field, not the kind of sentence; some records put a method description
# or a goal in their hypothesis field, and the page shows it under 'Stated hypothesis:'.
CARD_LABEL = (
    "Quoted from the PSI record by the team's code (code written with an AI assistant); no language "
    "model wrote or changed this text. Each quote carries a label that names the record field it comes "
    "from, so a stated hypothesis or objective is not read as a finding; the sentence under the label is "
    "NASA's wording, whatever that field says. The quotes are picked by fixed rules and are not a summary "
    "of results.")

# The four contract queries (contracts/README.md), in the order the files are written.
QUERIES = (
    ("iss", "ISS"),
    ("lunar_habitat", "lunar habitat"),
    ("spacesuit", "spacesuit"),
    ("mars_habitat", "Mars base"),
)

# pipeline/spec/scenarios.json _meta.status_rule: six values. Anything else stops the build.
STATUSES = ("in_atmosphere", "oxygen_only", "pressure_only", "other_atmosphere",
            "not_measured", "atmosphere_not_specified")
# pipeline/spec/statements.json 'gap': nine gap codes (the two flow codes were added by the data role's
# audit of 14 November). Anything else stops the build.
GAP_CODES = ("pressure:not_recorded", "oxygen:not_recorded",
             "oxygen:no_usable_test_in_range", "pressure:no_usable_test_in_range",
             "flow:not_recorded", "flow:no_usable_test_in_range",
             "gravity:no_usable_test_at_lunar", "gravity:no_usable_test_at_martian",
             "need:no_usable_test")
# gap code -> id of the pipeline's fixed sentence for it in data/pipeline/evidence/scenario_<id>.json.
# oxygen:not_recorded and pressure:not_recorded keep the team clause, which also says whether the
# variable is not a column of the table or an empty or flagged cell; need:no_usable_test is said by
# the status sentence.
GAP_PIPELINE_SENTENCE = {
    "oxygen:no_usable_test_in_range": "gap.oxygen.no_usable_test_in_range",
    "pressure:no_usable_test_in_range": "gap.pressure.no_usable_test_in_range",
    "flow:not_recorded": "gap.flow.not_recorded",
    "flow:no_usable_test_in_range": "gap.flow.no_usable_test_in_range",
    "gravity:no_usable_test_at_lunar": "gap.gravity.no_usable_test_at_level",
    "gravity:no_usable_test_at_martian": "gap.gravity.no_usable_test_at_level",
}
STATUS_PIPELINE_SENTENCE = {s: f"status.{s}" for s in STATUSES}
READING_LEAD = "What a count of this need means (the pipeline's reading): "

VARIABLE_WORD = {"o2_pct": "oxygen", "pressure_kpa": "pressure"}
GRAVITY_WORD = {"lunar": "lunar", "martian": "Martian"}

# row_unit values in pipeline/spec/sources.json that are not 'test'
ROW_UNITS = ("test", "test_day", "planned_matrix", "session", "dataset_index")


# ------------------------------------------------------------------ small helpers

def num(x):
    """A number as written in text: 22.2 stays 22.2, 40.0 becomes 40."""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def plural(n, one, many=None):
    return one if n == 1 else (many or one + "s")


def join_and(items):
    items = list(items)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]


def cap(s):
    return s[:1].upper() + s[1:] if s else s


def inv_name(acc, acronym):
    return f"{acc} ({acronym})" if acronym else acc


def _bound(r, unit):
    lo, hi = r.get("min"), r.get("max")
    sep = "" if unit == "%" else " "
    lo_inc = r.get("min_inclusive", True)
    hi_inc = r.get("max_inclusive", False)
    if lo is not None and hi is not None:
        lo_txt = num(lo) if lo_inc else f"above {num(lo)}"
        hi_txt = num(hi) if hi_inc else f"below {num(hi)}"
        return f"{lo_txt} to {hi_txt}{sep}{unit}"
    if hi is not None:
        return f"{'up to' if hi_inc else 'below'} {num(hi)}{sep}{unit}"
    if lo is not None:
        return f"{num(lo)}{sep}{unit} or more" if lo_inc else f"above {num(lo)}{sep}{unit}"
    return None


def bins_text(ranges):
    """'oxygen 30 to 36%, pressure below 85.8 kPa' from a scenarios.json 'ranges' block, or None."""
    parts = []
    if ranges.get("o2_pct"):
        parts.append("oxygen " + _bound(ranges["o2_pct"], "%"))
    if ranges.get("pressure_kpa"):
        parts.append("pressure " + _bound(ranges["pressure_kpa"], "kPa"))
    return ", ".join(parts) if parts else None


def flow_text(ranges):
    """'5 to 30 cm/s' from the flow range of a scenario, or None."""
    return _bound(ranges["flow_cms"], "cm/s") if ranges.get("flow_cms") else None


def kind_noun(fuel_phase, geometry, n):
    """What a group of tests is, for the count-by-phase clauses."""
    if fuel_phase == "liquid" and geometry == "droplet":
        return plural(n, "fuel-droplet test")
    if fuel_phase == "gas" and geometry == "spherical burner":
        return plural(n, "gas-burner flame")
    if fuel_phase == "gas" and geometry == "gas jet":
        return plural(n, "gas-jet flame")
    if fuel_phase == "solid":
        return plural(n, "solid-material test")
    if fuel_phase in ("liquid", "gas"):
        return plural(n, f"{fuel_phase}-fuel test")
    raise ValueError(f"no wording for fuel_phase={fuel_phase!r}, geometry={geometry!r}")


# ------------------------------------------------------------------ need statements

def lead(ranges):
    b = bins_text(ranges)
    return f"Recorded tests (team count; team bins: {b})." if b else \
        "Recorded tests (team count; no team bins: the pipeline sets no oxygen or pressure range for this scenario)."


def by_investigation(by_inv, n=None, single=None):
    # reader: after the pipeline's two-sentence status ('58 of the 136 ... No counted test was recorded with
    # oxygen and pressure both inside the ranges.') a bare 'By investigation:' read as a breakdown of the
    # zero; the clause now names the tests it breaks down
    if n is None:
        return f"By investigation: {by_inv}."
    if single:
        return (f"All {n} come from {single}." if n != 1 else f"It comes from {single}.")
    return f"The {n} by investigation: {by_inv}."


def status_in_atmosphere(a, u, by_kind):
    return f"{a} of the {u} tests usable for this need have recorded oxygen and pressure inside the bins: {by_kind}."


def _of(k, u):
    return f"All {u} usable tests have" if k == u and u > 1 else f"{k} of the {u} usable tests {plural(k, 'has', 'have')}"


def status_oxygen_only(o, u, by_inv, pressure_sentence):
    return f"{_of(o, u)} recorded oxygen inside the bins ({by_inv}); {pressure_sentence}."


def status_pressure_only(p, u, by_inv, oxygen_sentence):
    return f"{_of(p, u)} recorded pressure inside the bins ({by_inv}); {oxygen_sentence}."


def status_other_atmosphere(u):
    return f"None of the {u} usable tests has recorded oxygen and pressure inside the bins."


def status_not_measured(n_investigations):
    return (f"No test is counted: no investigation among the {n_investigations} both states this need "
            "as an objective and records the variables it requires.")


def status_atmosphere_not_specified(u):
    # review: 'usable for this need at any atmosphere' could be read as 'applies to any atmosphere'
    return (f"No test is counted as matching this scenario's atmosphere. {u} {plural(u, 'test is', 'tests are')} "
            "usable for this need when the atmosphere is left out of the count.")


def further_oxygen_only(o, by_inv, pressure_sentence):
    # review: 'no recorded pressure' was wrong for a cell that holds a value the pipeline does not use
    return (f"A further {o} {plural(o, 'has', 'have')} recorded oxygen inside the bins and no pressure "
            f"value the count can use ({by_inv}); {pressure_sentence}.")


def further_pressure_only(p, by_inv):
    return (f"A further {p} {plural(p, 'has', 'have')} recorded pressure inside the bins and no oxygen value "
            f"the count can use ({by_inv}).")


def basis_clause(u, x, y):
    return (f"Of the {u} usable tests, {x} have ambient oxygen and {y} are inverse-flame tests whose oxygen "
            "is the burner stream and cannot match a crew atmosphere.")


def phase_clause(n, noun_many, solid):
    head = "It is" if n == 1 else f"All {n} are"
    if solid:
        return f"{head} {noun_many}."
    return f"{head} {noun_many}; none is a solid-material test."


def not_a_column(variable, tables):
    """'pressure is not a column in the PSI experimental tables of PSI-25 (BASS-II) and ...'"""
    t = plural(len(tables), "table")
    return f"{VARIABLE_WORD[variable]} is not a column in the PSI experimental {t} of {join_and(tables)}"


def cell_empty(variable, k, tables):
    return (f"the {VARIABLE_WORD[variable]} cell is empty for {k} {plural(k, 'test')} in the PSI experimental "
            f"{plural(len(tables), 'table')} of {join_and(tables)}")


FLAG_WORDS = {"out_of_range": "out of range", "not_a_number_in_source": "not a number",
              "unreadable": "unreadable"}


def cell_not_used(variable, k, tables, cells, column, flag):
    """review: a cell that holds a value the pipeline does not use is not an empty cell. FLEX test 114
    has '0' in 'Ambient pressure; mmHg'; the pipeline flags it out_of_range and uses no pressure.
    cells: the distinct cell texts as written (None when they could not be read back)."""
    v = VARIABLE_WORD[variable]
    reason = FLAG_WORDS.get(flag, flag.replace("_", " "))
    where = f"in the PSI experimental {plural(len(tables), 'table')} of {join_and(tables)}"
    if cells and column:
        shown = join_and(f"'{c}'" for c in cells)
        return (f"the {v} {plural(k, 'cell', 'cells')} of {k} {plural(k, 'test')} {where} "
                f"{plural(k, 'reads', 'read')} {shown} (column '{column}'), which the team pipeline flags as "
                f"{reason} and does not use as a {v}")
    return (f"the team pipeline flags the {v} {plural(k, 'cell', 'cells')} of {k} {plural(k, 'test')} {where} "
            f"as {reason} and uses no {v} value for {plural(k, 'it', 'them')}")


def balance_diluted(k, c, h, b, zero, n):
    parts = [f"{c} carbon dioxide", f"{h} helium"] + ([f"{b} both"] if b else [])
    s = f"Of these {n}, {k} {plural(k, 'has', 'have')} carbon dioxide or helium added to the atmosphere ({', '.join(parts)})"
    if zero:
        s += f"; the other {zero} {plural(zero, 'has a', 'have')} recorded carbon dioxide and helium {plural(zero, 'fraction', 'fractions')} of zero"
    return s


def balance_zero(zero, n):
    if zero == n:
        return (f"All {n} have recorded carbon dioxide and helium fractions of zero" if n != 1 else
                "It has recorded carbon dioxide and helium fractions of zero")
    return f"{zero} of these {n} have recorded carbon dioxide and helium fractions of zero"


def balance_no_column(k, tables, measured_co2_tables=()):
    s = (f"added carbon dioxide or helium is not a column in the PSI experimental "
         f"{plural(len(tables), 'table')} of {join_and(tables)}, so the balance gas of {k} "
         f"{plural(k, 'test')} is not in the table")
    if measured_co2_tables:
        s += (f" (the {plural(len(measured_co2_tables), 'table')} of {join_and(measured_co2_tables)} "
              f"{plural(len(measured_co2_tables), 'has', 'have')} measured initial and final carbon dioxide "
              "readings, which the team pipeline does not read as added gas)")
    return s


def balance_empty(k):
    return f"the carbon dioxide and helium cells are empty for {k} {plural(k, 'test')}"


def balance_one_column(k, tables):
    return (f"only one of carbon dioxide and helium is a column for {k} {plural(k, 'test')} "
            f"({join_and(tables)}), so their balance gas is not fully in the table")


MEASURED_NOT_IN_TABLE = "the PSI {records} of {ids} {say} pressure was measured; the value is not in the table"


def measured_not_in_table(ids):
    many = len(ids) > 1
    return MEASURED_NOT_IN_TABLE.format(records="records" if many else "record", ids=join_and(ids),
                                        say="say" if many else "says")


def no_usable_in_range(variable):
    return f"No usable test has recorded {VARIABLE_WORD[variable]} inside the bins."


def gravity_sentence(level):
    return (f"Every test in the PSI tables is a microgravity test; none was run at "
            f"{GRAVITY_WORD[level]} gravity.")


def outside_objective(k, ids, includes_stream=False, further=True):
    one = len(ids) == 1
    # reader: 'further' only where tests are counted; after 'no test is counted' it pointed at nothing
    s = (f"{k} {'further ' if further else ''}{plural(k, 'test records', 'tests record')} the needed variables, but "
         f"{'the investigation' if one else 'the investigations'} ({join_and(ids)}) {'does' if one else 'do'} "
         f"not state this need as an objective; {plural(k, 'it is', 'they are')} not counted.")
    if includes_stream:
        # review: 139 of the 272 PSI-159 tests outside S1's stated objective are inverse flames
        s += (" These include inverse-flame tests, whose oxygen value is the burner stream and not an "
              "atmosphere.")
    return s


def join_or(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]


def test_end_clause(n, tally, none_extinction):
    if none_extinction:
        # review (14 Nov): said as what the tests ended in, so 'disruption' is not read as an extinction
        ends = join_or(f"{v} ({c})" for v, c in tally)
        head = f"The {n} matched tests ended in" if n != 1 else "The matched test ended in"
        return f"{head} {ends}; none is recorded as an extinction."
    body = ", ".join(f"{c} {v}" for v, c in tally)
    return f"Recorded test ends of these {n}: {body}." if n != 1 else f"Recorded test end: {body}."


TEST_END_NOTES = {
    # reader: the FLEX table does not define its 'Test end' words, so the note says what the table shows
    # (separate values of the column) and what the page does with them, not what a disruption is
    "disruption": ("'Disruption' and 'extinction' are separate values of the table's 'Test end' column; a "
                   "disruption is not read here as a flame extinction."),
    "flow termination": "'Flow termination' is the recorded end of the test, not a flame extinction.",
}


# ------------------------------------------------------------------ frames

def frame_bins(label, ranges):
    b = bins_text(ranges)
    if not b:
        return (f"The pipeline sets no oxygen or pressure range for the {label} scenario, so no recorded test is "
                "counted as matching its atmosphere.")
    # reader: 'counts ... are recorded tests whose oxygen and pressure fall in the team bins' was not true of
    # the oxygen-only counts (ISS P1 and P3: oxygen inside the bin, no pressure value in the table)
    s = (f"For the {label} scenario, the oxygen and pressure recorded for each test are compared with the "
         f"team bins ({b}); the bins are the team's choice. A test whose table holds no pressure value, or no "
         "oxygen value, is reported apart and is never placed inside a bin.")
    f = flow_text(ranges)
    if f:
        s += (f" The scenario also sets a flow range ({f}); the flow speed of the matched tests is compared with "
              "it and does not change the counts.")
    return s


# review: which objective sentence backs which need is the team pipeline's reading, so it is said.
FRAME_RULE = ("A test is counted for a need only if its investigation's PSI record states that need "
              "as an objective (objective sentences are linked to needs by the team pipeline).")
# reader: says what an inverse-flame oxygen value is, in the words of pipeline/spec/variables.json (o2_basis)
FRAME_STREAM = ("Inverse-flame tests, whose oxygen value is the burner stream (the gas issuing from the burner, "
                "not the surrounding atmosphere), are never matched to a crew atmosphere.")


# review: 'PSI has no partial-gravity combustion data' spoke for all of PSI; the claim the code can
# check is about the test tables, with the team's own gravity classification, and it is worded so.
FRAME_GRAVITY = ("Every test in the PSI test tables is a microgravity test (gravity level set per table by the "
                 "team from the PSI record); the tables hold no partial-gravity test, and microgravity and 1 g "
                 "results are not shown here as bounds for lunar or Martian gravity.")


def nasa_gravity_gap(quote):
    """The NASA sentence behind the gravity gap, quoted as written in its reference item (TB008.gaps);
    without a quote field the item's own summary is used, unquoted."""
    if quote:
        return f"NASA's fire protection technical brief OCHMO-TB-008 says: \"{quote}\" (TB008.gaps)."
    return ("NASA's fire protection technical brief OCHMO-TB-008 names material flammability in partial gravity "
            "a major gap (TB008.gaps).")


def frame_drop_tests(level, below_one_g, below_both, seconds, criteria_caveat, ai_read, n_materials=None,
                     on_ntrs=False):
    """review: Olson and Ferkul's Table I (references.json OF2012.table1, checked by the data role at 12:47),
    placed in the frame of a lunar or Martian scenario as the design planned (A2 (1)), and only there.
    below_one_g / below_both are 'every' or 'some': the materials whose two low-gravity limits (ULOI*,
    MOC*) at this level are lower than both 1 g limits, and also lower than both 0 g limits. No limit
    value is printed; the drop duration and the paper's caveat on the criteria are kept, and the paper's
    Fig. 6 averages are not used.
    reader: the item does not say whose drop tower it was, so 'NASA drop-tower tests' became 'a paper on the
    NASA Technical Reports Server' (only when the reference url is on ntrs.nasa.gov); the number of
    materials is said ('every material' of a table of three), and a limiting oxygen concentration is
    explained in the item's own terms (ULOI*: the minimum at which the flame survived the full drop;
    MOC*: the maximum at which it self-extinguished)."""
    g = GRAVITY_WORD[level]
    paper = "a paper on the NASA Technical Reports Server" if on_ntrs else "a published paper"
    n_word = NUMBER_WORD.get(n_materials, str(n_materials)) if n_materials else None
    mats = f"{n_word} materials" if n_word and n_materials > 1 else "the materials of the table"
    s = (f"Outside PSI, Table I of {paper} (Olson and Ferkul, NTRS-20130010991) gives limiting oxygen "
         "concentrations (the oxygen level below which the flame did not keep burning in the test) for "
         f"{mats}; ")
    each = {"every": "for each of them", "some": "for some of them"}
    if below_both == below_one_g:
        s += f"{each[below_both]}, both limits at {g} gravity are lower than those at 1 g and at 0 g"
    else:
        s += f"{each[below_one_g]}, both limits at {g} gravity are lower than those at 1 g"
        if below_both:
            s += f", and {each[below_both]} they are lower than those at 0 g as well"
    s += "."
    if seconds is not None:
        s += f" These low-gravity limits come from {num(seconds)} s drop-tower tests"
        if criteria_caveat:
            s += ", and the paper says their extinction criteria are not the same as in 1 g"
        s += "; the table was read by an AI assistant and not checked by a person" if ai_read else ""
    elif ai_read:
        s += " The table was read by an AI assistant and not checked by a person"
    return s + " (OF2012.table1)."


# reader (coord/decisions.md 14:15): the lunar-habitat pressure bin reaches above the 10.2 psi of the
# challenge statement, so the frame says what no counted test was recorded at, and where the matched ones were.
def _span(lo, hi, unit, sep=" "):
    return f"{num(lo)}{sep}{unit}" if lo == hi else f"{num(lo)} to {num(hi)}{sep}{unit}"


def _above(lo, hi):
    return f"about {num(lo)} kPa above it" if lo == hi else f"{num(lo)} to {num(hi)} kPa above it"


def frame_challenge_bound(o2_min, psi, kpa, hedge, from_copy, n_below, inside):
    """inside: None, or {n, noun, o2 (lo, hi), kpa (lo, hi), atm, above (lo, hi) or None} for the counted
    tests inside the team bins. The challenge statement's hedge word ('expected', 'likely') is kept."""
    where = "CH.moonbase, read from a copy" if from_copy else "CH.moonbase"
    what = f"the {hedge} Moon Base atmosphere" if hedge else "the Moon Base atmosphere"
    s = (f"The challenge statement names {num(o2_min)}% oxygen or more and {num(psi)} psi ({num(kpa)} kPa) or "
         f"less as {what} ({where}); the team's pressure bin is wider than that. ")
    at = f"at {num(o2_min)}% oxygen or more and at or below {num(psi)} psi"
    s += (f"No counted test was recorded {at}" if n_below == 0 else
          f"{n_below} counted {plural(n_below, 'test was', 'tests were')} recorded {at}")
    if inside:
        atm = f" (about {num(inside['atm'])} atm)" if inside.get("atm") is not None else ""
        s += (f": the {inside['n']} counted {plural(inside['n'], 'test')} inside the bins "
              f"{plural(inside['n'], 'is a', 'are')} {inside['noun']} recorded at "
              f"{_span(*inside['o2'], '%', '')} oxygen and {_span(*inside['kpa'], 'kPa')}{atm}")
        if inside.get("above"):
            s += ", " + _above(*inside["above"])
    return s + "."


def matched_bound_clause(n, o2, kpa, atm, above, psi, bound_kpa, o2_min, n_below):
    """The same caveat next to the count in a need statement (decision 14:15: 'the caveat is shown wherever
    the count is'). above is None when the tests are not all above the challenge-statement pressure."""
    atm_txt = f" (about {num(atm)} atm)" if atm is not None else ""
    s = (f"{'These ' + str(n) + ' were' if n != 1 else 'It was'} recorded at {_span(*o2, '%', '')} oxygen and "
         f"{_span(*kpa, 'kPa')}{atm_txt}")
    if above:
        s += (f", which is inside the team's pressure bin and {_above(*above).replace(' above it', '')} above the "
              f"{num(psi)} psi ({num(bound_kpa)} kPa) of the challenge statement (CH.moonbase)")
    at = f"at {num(o2_min)}% oxygen or more and at or below {num(psi)} psi"
    s += (f"; no counted test was recorded {at}." if n_below == 0 else
          f"; {n_below} counted {plural(n_below, 'test was', 'tests were')} recorded {at}.")
    return s


def bound_short(kpa, psi, bound_kpa):
    """Short form for a gap line or a result note that repeats the count."""
    return (f"recorded at {_span(*kpa, 'kPa')}, above the {num(psi)} psi ({num(bound_kpa)} kPa) of the challenge "
            "statement")


def flow_outside(n):
    # reader: the pipeline's flow sentence gives the tests inside the range and those with no flow value;
    # the rest were left to subtraction
    return (f"The other {n} {plural(n, 'was', 'were')} recorded with a flow speed outside that range.")


def frame_mars(eawg_pairs):
    # review: no 'recommends', even in an attribution; the report's own caveat is kept
    atm = join_and(f"{p:.1f} psia ({k} kPa)" for p, k in eawg_pairs)
    return ("The scorer preset for this scenario sets no atmosphere. NASA's Exploration Atmospheres Working "
            f"Group report lists {atm}, each with 32% oxygen, among its nominal atmospheres for surface "
            "habitats and says they are not requirements (EAWG.atmospheres); the kPa values are the team's "
            "conversion, and the preset does not use these atmospheres.")


def frame_spacesuit(max_ambient, max_stream):
    return (f"The highest ambient oxygen in any test in the PSI tables is {num(max_ambient)}% (computed from "
            f"the tables); higher oxygen values, up to {num(max_stream)}%, are the burner stream of inverse "
            "flames, not the surrounding atmosphere.")


# ------------------------------------------------------------------ result notes

def note_phase(fuel_phase, surrogate_for):
    if fuel_phase == "gas" and surrogate_for == "solid":
        # review: the PSI-20 record says 'condensed fuels' (a solid, or a liquid in an inert matrix)
        return ("Gas-burner flame study whose burner emulates condensed fuels; not a test of solid "
                "cabin materials (team catalog classification).")
    fixed = {
        "gas": "Gas-fuel flame configuration; not a test of solid cabin materials (team catalog classification).",
        "liquid": "Liquid-fuel configuration; not a test of solid cabin materials (team catalog classification).",
        "solid": "Solid-fuel configuration (team catalog classification).",
        "aerosol": "Aerosol configuration; not a flame test of solid cabin materials (team catalog classification).",
    }
    if fuel_phase not in fixed:
        raise ValueError(f"no note wording for fuel_phase={fuel_phase!r}")
    return fixed[fuel_phase]


def note_test_ambient(k, n_amb, k_oxy, pressure_part, caveat=None):
    head = (f"None of its {n_amb} tests with recorded ambient oxygen has" if k == 0 else
            f"{k} of its {n_amb} tests with recorded ambient oxygen {plural(k, 'has', 'have')}")
    s = f"{head} oxygen and pressure inside this scenario's team bins"
    if caveat:  # reader: decision 14:15, the caveat goes wherever the count is shown
        s += f" ({caveat})"
    if k_oxy:
        s += (f"; {k_oxy} {plural(k_oxy, 'has', 'have')} recorded oxygen inside the bins and no pressure value "
              "the count can use")
    if pressure_part:
        s += f"; {pressure_part}"
    return s + "."


def note_test_no_ambient(n_all, missing):
    return (f"Its PSI {plural(1, 'table')} lists {n_all} {plural(n_all, 'test')}, and {missing}, so none can be "
            "matched to this scenario's team bins.")


def note_stream(m):
    return (f"Its {m} inverse-flame {plural(m, 'test is', 'tests are')} not matched to this scenario's "
            "atmosphere, because the oxygen value, where recorded, is the burner stream and not the "
            "surrounding gas.")


def note_test_no_ranges(n_all):
    return (f"Its PSI tables list {n_all} {plural(n_all, 'test')}; this scenario sets no oxygen or pressure "
            "range, so none is matched to an atmosphere.")


def note_test_day(days, flames):
    extra = f", {flames} flames ignited in all" if flames is not None else ""
    return (f"PSI's table for this investigation has one row per test day ({days} test days{extra}), so its "
            "tests cannot be matched one by one")


def note_test_day_oxygen(lo, hi, as_written, approximate_ignited=False):
    # review: the PSI-20 table notes call these 'approximate concentrations for tests that ignited',
    # not settings; the count of odd cells is no longer printed (it was not in the facts block)
    what = ("the oxygen concentrations listed (approximate, for the tests that ignited, as the table's notes say)"
            if approximate_ignited else "the oxygen values listed")
    s = f"{what} run from {num(lo)} to {num(hi)}%"
    if as_written:
        cells = join_and(f"'{c}'" for c in as_written)
        # reader: 'are quoted as written' did not say that the cells are left out of the range
        s += (f" (the cells {cells}, shown as written in the table, are not used for this range)"
              if len(as_written) > 1 else
              f" (the cell {cells}, shown as written in the table, is not used for this range)")
    return s


def note_test_day_pressure(phrase):
    return f"the table's notes say the chamber pressures were varied but are '{phrase}'"


NOTE_ROW_UNIT = {
    "planned_matrix": ("PSI's table for this investigation lists planned ranges of conditions per fuel "
                       "({rows} rows), not individual tests, so it cannot be matched test by test."),
    "session": ("PSI's table for this investigation has one row per sampling session ({rows} rows) and lists "
                "no combustion test."),
    "dataset_index": ("PSI's table for this investigation is an index of figures in publications ({rows} rows), "
                      "not a table of tests."),
}
NOTE_NO_TABLE = "PSI holds no experimental table for this investigation."


def note_objectives(needs):
    """needs: list of 'P1 (Flammability limit)' strings."""
    if not needs:
        return "The team pipeline links none of the needs to an objective stated in this record."
    word = plural(len(needs), "need")
    return f"The team pipeline links {word} {join_and(needs)} to objectives stated in this record."


def note_tie(names):
    return f"Tied with {join_and(names)} under the team's current weights."


NOTE_NEAR = ("Listed because its team score is level with or close to the results shown, under the team's "
             "current weights.")


def note_assumed(dims):
    # review: says that the assumed value is used by the ranking only and is not a recorded value
    words = {"O2": "oxygen", "pressure": "pressure"}
    what = " or ".join(words[d] for d in dims)
    return (f"The catalog reports no {what} for this configuration; for the ranking only, the scorer assumed "
            "ordinary cabin air (a team assumption, not a recorded value). The counts on this page never fill "
            "in a missing value.")


def note_spacesuit(lo, hi):
    # review: no rank word ('the first two'); the build checks that an inverse flame is among the results
    return (f"No test in the PSI tables has oxygen inside this scenario's team bin ({num(lo)} to {num(hi)}%); the "
            "results are listed for completeness, and the inverse flames among them record burner-stream "
            "oxygen, not an atmosphere.")


NOTE_MARS = ("The preset sets no atmosphere, so the ranking compares only flow and research purpose (with "
             "ventilation assumed), not oxygen or pressure; it is not a match to a Mars habitat.")


# ------------------------------------------------------------------ gaps

def gap_gravity(level, quote):
    # review: 'are not bounds' was stated as the team's own finding with a source (TB008.gaps) that does
    # not say it; the page now says what it does (it does not treat them as bounds) and quotes NASA.
    g = GRAVITY_WORD[level]
    return (f"Every test in the PSI tables is a microgravity test; none was run at {g} gravity, and "
            f"microgravity and 1 g results are not treated here as bounds for {g} gravity. "
            + nasa_gravity_gap(quote))


def gap_gravity_needed(level):
    return f"test-level records in PSI from combustion tests run at {GRAVITY_WORD[level]} gravity"


def gap_solid(n_inv, max_solid_o2, no_o2_tables=()):
    # review: 'no solid-sample test has an oxygen value above 22.2%' left out that several solid-sample
    # tables record no oxygen at all
    s = (f"In the PSI experimental tables of the {n_inv} investigations, no solid-sample test has a recorded "
         f"oxygen value above {num(max_solid_o2)}%, and pressure is not a column in any solid-sample table.")
    if no_o2_tables:
        s += (f" Oxygen is not a column in the solid-sample {plural(len(no_o2_tables), 'table')} of "
              f"{join_and(no_o2_tables)}.")
    return s


def gap_solid_psi20(max_setting, pressure_not_identified=False):
    # review: the table lists approximate concentrations for tests that ignited, per test day
    s = ("PSI's test-day table for PSI-20, a gas-burner study that emulates condensed fuels, lists approximate "
         f"oxygen concentrations up to {num(max_setting)}%")
    if pressure_not_identified:
        s += " and does not identify the chamber pressures"
    return s + "; these are gas flames, not tests of solid materials."


NUMBER_WORD = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def gap_solid_saffire(samples, n_samples, n_inv, ai_read, paper_title=None):
    """review: written from the Saffire IV to VI item the data role checked at 12:47 (SAF456.conditions),
    only for the samples whose oxygen and pressure fall inside the scenario's team bins. The data role's
    caveats are kept: the values are called the sample test conditions of Table 1 (the paper's own title),
    never measured values or set points; the table covers the samples considered in that paper, not every
    Saffire IV to VI sample; numbers are cited, nothing longer is quoted. samples: [(id, o2, kPa)]."""
    listed = join_and(f"{sid} ({o2:.1f} mol % oxygen, {kpa:.1f} kPa)" for sid, o2, kpa in samples)
    # reader: 'ICES-2024-365' alone told a reader nothing; the paper's title is taken from references.json
    paper = f"the paper '{paper_title}' (ICES-2024-365)" if paper_title else "ICES-2024-365"
    s = (f"Outside PSI, Table 1 of {paper} lists the sample test conditions of the "
         f"{NUMBER_WORD.get(n_samples, str(n_samples))} Saffire IV to VI samples considered in that paper; "
         f"{plural(len(samples), 'sample')} {listed} {plural(len(samples), 'is', 'are')} inside this scenario's "
         f"team bins. None of the {n_inv} PSI investigations used here is one of these flights, and these samples "
         "are not in any count on this page.")
    if ai_read:
        s += " The table was read by an AI assistant and not checked by a person."
    return s


GAP_SOLID_NEEDED = "test-level records in PSI for solid samples with both oxygen and pressure at these atmospheres"


def gap_phase(n, inv_names, caveat=None):
    s = (f"The {n} tests inside this scenario's team bins for extinction conditions (S1) are all "
         f"fuel-droplet tests ({join_and(inv_names)}); none is a solid-material or gas-burner test.")
    if caveat:  # reader: decision 14:15, the caveat goes wherever the count is shown
        s += f" They were {caveat}."
    return s


GAP_PHASE_NEEDED = ("test-level records in PSI of extinction tests with solid materials or gas flames, with "
                    "oxygen and pressure inside these bins")


def gap_detection(d2_u, d2_inv, d2_missing, d1_not_measured, d1_stated=False, n_inv=None):
    # reader: 'counted for', the word the need statements use ('usable' was the older word for the same tests)
    s = (f"For detection, the {d2_u} smoke {plural(d2_u, 'test')} counted for smoke generation conditions (D2, "
         f"{join_and(d2_inv)}) {plural(d2_u, 'has', 'have')} neither oxygen nor pressure in the table"
         if d2_missing else
         f"For detection, {d2_u} smoke {plural(d2_u, 'test is', 'tests are')} counted for smoke generation "
         f"conditions (D2, {join_and(d2_inv)})")
    if d1_not_measured:
        # review: which objective backs which need is the team pipeline's reading
        s += (f", and no investigation among the {n_inv} both states the measurement of combustion products "
              "(D1) as an objective and records the variables it needs" if d1_stated else
              f", and the team pipeline finds no investigation among the {n_inv} whose PSI record states the "
              "measurement of combustion products (D1) as an objective")
    # review: the item says detection systems 'are based on inadequate knowledge of ...'; worded as that
    return s + (". The NASA workshop report NASA/CP-2003-212103 describes knowledge of the fire signatures of "
                "spacecraft materials, and of the effect of low gravity on them, as inadequate for detection "
                "systems (CP2003.detection).")


GAP_DETECTION_NEEDED = ("test-level records in PSI of smoke and combustion-product measurements with the "
                        "oxygen and pressure of the test atmosphere")


def gap_not_covered(area, why):
    return f"{area}: {why}"


GAP_NOT_COVERED_NEEDED = "measurements of this kind in the PSI experimental tables"


# ------------------------------------------------------------------ cards

def card_summary(quotes):
    """quotes: one or two verbatim objective spans."""
    return "Quoted from the PSI record. Stated objective: " + " ".join(f'"{q}"' for q in quotes)


def key_point(label, quote):
    return f'{label} "{quote}"'


def license_note(lic):
    if lic == "not stated in the record":
        return "Licence: not stated in the PSI record."
    return f"Licence of the PSI record: {lic}."
