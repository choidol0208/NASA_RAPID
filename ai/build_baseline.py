# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Baseline product files, written by code with no language model (design component A2).

    python3 ai/build_baseline.py            build and write both files, print the iss and lunar text
    python3 ai/build_baseline.py --print-all  also print spacesuit and mars_habitat
    python3 ai/build_baseline.py --check    build and compare with the files on disk, write nothing

Writes
  data/insights/scenarios.json  one entry per contract query (iss, lunar_habitat, spacesuit, mars_habitat):
                                frame, one need statement per need id in pipeline/spec/needs.json, gaps,
                                result notes for the live top 3 of scoring.scorer.rank plus near-ties
  data/insights/cards.json      24 quoted cards (status 'fallback_quote'): the first quotable objective
                                sentence(s) and the first quotable approach, hypothesis and impact sentence,
                                each verbatim with its record-field label
  data/insights/_meta.json      the disclosure block of both files (they are arrays, so it lives only there)

Every number in the text is counted here from data/pipeline/*.csv and the NASA tables and goes into the
item's 'facts'. The counts are recounted from tests.csv, need_tests.csv and scenario_tests.csv and must equal
scenario_needs.csv, or the build stops. An unknown status or gap code stops the build. Every source string
must resolve through ai/resolve.py, or the build stops. Nothing in scoring/ is changed; rank() is imported.
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import config, meta as metamod, evidence as evmod, resolve as resmod, templates as T  # noqa: E402

ROOT = config.ROOT
OUT_SCENARIOS = config.INSIGHTS_DIR / "scenarios.json"
OUT_CARDS = config.INSIGHTS_DIR / "cards.json"

F_TESTS = "data/pipeline/tests.csv"
F_NEED_TESTS = "data/pipeline/need_tests.csv"
F_SCEN_TESTS = "data/pipeline/scenario_tests.csv"
F_SCEN_NEEDS = "data/pipeline/scenario_needs.csv"
F_OBJ_LINKS = "data/pipeline/objective_links.csv"
F_NEEDS = "pipeline/spec/needs.json"
F_SCENARIOS = "pipeline/spec/scenarios.json"
F_SOURCES = "pipeline/spec/sources.json"
F_REFS = "pipeline/spec/references.json"
F_VARIABLES = "pipeline/spec/variables.json"
F_SCORING = "scoring/scoring_config.json"
F_CONFIGS = "data/catalog/configurations.csv"
F_INVEST = "data/catalog/investigations.csv"
F_MANIFEST = "data/psi/manifest.json"
F_EVIDENCE = "data/insights/evidence.json"
F_PACKAGES = "data/pipeline/evidence"
TABLE_DIR = "data/psi/experimental_tables"

SCENARIO_INPUTS = (F_SCEN_NEEDS, F_SCEN_TESTS, F_NEED_TESTS, F_TESTS, F_NEEDS, F_SCENARIOS)


def package_files():
    """Repo paths of the data role's scenario evidence packages (data/pipeline/evidence/index.json)."""
    idx = _json(f"{F_PACKAGES}/index.json")
    return [f"{F_PACKAGES}/{p['file']}" for p in idx["packages"] if p.get("kind") == "scenario"]
NEAR_TIE_POINTS = 3.0  # design A2 (4): within 3 points of the third result, strictly
KPA_PER_PSI = 6.894757
KPA_PER_ATM = 101.325
CHALLENGE_ITEM = "CH.moonbase"  # references.json: the challenge statement's Moon Base atmosphere
MEASURED_PRESSURE = re.compile(r"\bmeasure\s+pressure\b", re.I)
SHORT_QUOTE_WORDS = 12  # design: add the next objective sentence when the first is under 12 words
READING_SAYS_NONE = re.compile(r"\bno test is counted\b", re.I)


class BuildStop(RuntimeError):
    """The inputs are not what the templates were written for; nothing is written."""


def stop(msg):
    raise BuildStop(msg)


def _csv(rel):
    with open(ROOT / rel, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _json(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def acc_key(acc):
    return int(acc.split("-")[1])


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def unique(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


# ====================================================================== inputs

class Ctx:
    def __init__(self):
        self.tests = _csv(F_TESTS)
        self.test = {t["test_id"]: t for t in self.tests}
        self.need_tests = _csv(F_NEED_TESTS)
        self.scen_tests = defaultdict(dict)
        for r in _csv(F_SCEN_TESTS):
            self.scen_tests[r["scenario_id"]][r["test_id"]] = r
        self.scen_needs = {(r["scenario_id"], r["need_id"]): r for r in _csv(F_SCEN_NEEDS)}
        # objective_links.csv (after the data role's literature check, commit a5a9e87): a link rests on a purpose
        # sentence of the PSI record ('record_field', 'quote') and/or of a publication ('publication_item'), with a
        # 'verdict'; only 'supported' links are counted (pipeline/spec/needs.json _meta.stated_by_rule). A link
        # can have no record field (D1/PSI-25 rests on BASS2TM.products only), so a source is never built from
        # an empty field.
        self.obj_links_all = _csv(F_OBJ_LINKS)
        self.obj_links = [r for r in self.obj_links_all if (r.get("verdict") or "supported") == "supported"]
        self.needs_doc = _json(F_NEEDS)
        self.needs = self.needs_doc["needs"]
        self.need = {n["id"]: n for n in self.needs}
        self.scen = {s["id"]: s for s in _json(F_SCENARIOS)["scenarios"]}
        self.sources = _json(F_SOURCES)["sources"]
        self.source = {s["id"]: s for s in self.sources}
        self.sources_of = defaultdict(list)
        for s in self.sources:
            self.sources_of[s["investigation_id"]].append(s)
        self.refs, self.ref_doc = {}, {}
        for r in _json(F_REFS)["references"]:
            for it in r.get("items", []):
                self.refs[it["id"]] = it
                self.ref_doc[it["id"]] = r
        self.manifest = _json(F_MANIFEST)
        self.n_investigations = len(self.manifest["investigations"])
        self.configs = {c["config_id"]: c for c in _csv(F_CONFIGS)}
        self.scoring = _json(F_SCORING)
        self.ev = evmod.load(ROOT / F_EVIDENCE)
        self._records = {}
        self._bound = {}  # challenge_bound() per scenario
        self.warnings = []  # inconsistencies in inputs the pm role does not own (printed, not fixed)
        # the data role's evidence packages, one per scenario (fixed sentences and counts per need)
        self.package_path, self.package = {}, {}
        for rel in package_files():
            doc = _json(rel)
            sid = doc["environment"]["id"]
            self.package_path[sid], self.package[sid] = rel, doc

        if any(t["gravity_level"] != "microgravity" for t in self.tests):
            stop("a test in tests.csv is not a microgravity test: the gravity sentences no longer hold")

    def acronym(self, acc):
        return (self.ev["records"].get(acc) or {}).get("acronym") or ""

    def name(self, acc):
        return T.inv_name(acc, self.acronym(acc))

    def record(self, acc):
        if acc not in self._records:
            self._records[acc] = json.loads((config.PSI_CATALOG_DIR / f"{acc}.json").read_text(encoding="utf-8"))
        return self._records[acc]

    def source_vars(self, sid):
        s = self.source[sid]
        out = set(s.get("constants", {}))
        for c in s.get("columns", []):
            to = c["to"]
            out.update(to if isinstance(to, list) else [to])
        return out

    def table_name(self, sid):
        s = self.source[sid]
        # reader: one name per table. The file name spells SAFFIRE-2 where the PSI record's own acronym is
        # SAFFIRE-II, and the same statement used both; the record's acronym is used when the investigation
        # has one table, the file name only to tell two tables of one investigation apart.
        if len(self.sources_of[s["investigation_id"]]) == 1 and self.acronym(s["investigation_id"]):
            return self.name(s["investigation_id"])
        f = s["file"]
        name = f.split("Experimental table_", 1)[1] if "Experimental table_" in f else f
        name = name.rsplit(".", 1)[0].replace("_", " ")
        return f"{s['investigation_id']} ({name})"

    def tests_of(self, acc):
        return [t for t in self.tests if t["investigation_id"] == acc]

    def links_of(self, acc):
        return [r for r in self.obj_links if r["investigation_id"] == acc]

    def link_sources(self, r):
        """Source strings of one supported objective link: its objective_links.csv row, the PSI record field
        that holds the sentence (when the link has one) and the publication item (when it has one)."""
        acc, nid = r["investigation_id"], r["need_id"]
        out = [f"{F_OBJ_LINKS}#{nid}/{acc}"]
        if (r.get("record_field") or "").strip():
            out.append(f"{acc}.{r['record_field'].strip()}")
        if (r.get("publication_item") or "").strip():
            out.append(f"{F_REFS}#{r['publication_item'].strip()}")
        if len(out) == 1:
            stop(f"objective_links.csv {nid}/{acc}: a supported link with neither a record field nor a publication item")
        return out


# ====================================================================== recount

def recount(ctx, sc_id, need_id):
    """Recount one scenario_needs.csv row from need_tests.csv and scenario_tests.csv; stop on any difference."""
    row = ctx.scen_needs.get((sc_id, need_id))
    if row is None:
        stop(f"scenario_needs.csv has no row {sc_id}/{need_id}")
    stated = sorted({r["test_id"] for r in ctx.need_tests if r["need_id"] == need_id and r["objective_link"] == "stated"})
    outside = sorted({r["test_id"] for r in ctx.need_tests if r["need_id"] == need_id and r["objective_link"] != "stated"})
    marks = ctx.scen_tests[sc_id]
    tiers = {k: [t for t in stated if marks[t]["tier"] == k] for k in ("atmosphere", "oxygen_only", "pressure_only", "other")}
    got = {"usable_tests": len(stated), "tests_recorded_outside_objective": len(outside)}
    for k, ids in tiers.items():
        got[f"tests_{k}"] = len(ids)
        got[f"investigations_{k}"] = ";".join(sorted({ctx.test[t]["investigation_id"] for t in ids}, key=acc_key))
    sc = ctx.scen[sc_id]
    status = next((s for s, k in (("in_atmosphere", "atmosphere"), ("oxygen_only", "oxygen_only"),
                                  ("pressure_only", "pressure_only")) if tiers[k]),
                  "other_atmosphere" if stated else "not_measured")
    if not sc["ranges"].get("o2_pct") and not sc["ranges"].get("pressure_kpa"):
        status = "atmosphere_not_specified" if stated else "not_measured"
    got["status"] = status
    for k, v in got.items():
        if str(row[k]) != str(v):
            stop(f"recount differs from scenario_needs.csv for {sc_id}/{need_id} {k}: csv {row[k]!r}, recount {v!r}")
    if row["status"] not in T.STATUSES:
        stop(f"unknown status {row['status']!r} in scenario_needs.csv {sc_id}/{need_id}")
    codes = [c for c in row["gaps"].split(";") if c]
    for c in codes:
        if c not in T.GAP_CODES:
            stop(f"unknown gap code {c!r} in scenario_needs.csv {sc_id}/{need_id}")
    for t in tiers["atmosphere"] + tiers["oxygen_only"]:
        if ctx.test[t]["o2_basis"] != "ambient":
            stop(f"{t} is counted inside the oxygen bin for {sc_id}/{need_id} but its o2_basis is not ambient")
    # the evidence package must say the same: counts, status, gap codes and the matched tests
    pk = package_need(ctx, sc_id, need_id)
    c = pk["counts"]
    want = {"usable_tests": len(stated), "atmosphere": len(tiers["atmosphere"]),
            "oxygen_only": len(tiers["oxygen_only"]), "pressure_only": len(tiers["pressure_only"]),
            "other": len(tiers["other"]), "recorded_outside_objective": len(outside)}
    diff = {k: (c.get(k), v) for k, v in want.items() if c.get(k) != v}
    if diff or pk["status"] != row["status"] or sorted(g["code"] for g in pk["gaps"]) != sorted(codes):
        stop(f"evidence package {ctx.package_path[sc_id]} differs from scenario_needs.csv for {sc_id}/{need_id}: "
             f"{diff or ''} status {pk['status']} gaps {[g['code'] for g in pk['gaps']]}")
    matched = {m["test_id"]: m for m in pk["matched_tests"]}
    if set(matched) != set(tiers["atmosphere"] + tiers["oxygen_only"] + tiers["pressure_only"]):
        stop(f"evidence package matched_tests differ from the recount for {sc_id}/{need_id}")
    return {"row": row, "usable": stated, "outside": outside, "tiers": tiers, "status": row["status"], "gaps": codes,
            "package": pk, "matched": matched}


def package_need(ctx, sc_id, need_id):
    pk = ctx.package.get(sc_id)
    if pk is None:
        stop(f"no evidence package for scenario {sc_id} in {F_PACKAGES}/index.json")
    hits = [n for n in pk["needs"] if n["need_id"] == need_id]
    if len(hits) != 1:
        stop(f"{ctx.package_path[sc_id]}: {len(hits)} entries for need {need_id}")
    return hits[0]


def pipe_sentence(ctx, sc_id, need_id, stmt_id, required=True):
    """The pipeline's fixed sentence `stmt_id` for this scenario and need, as written, and its source
    string. Stops when it is missing (if required), not unique, or does not resolve to the same text."""
    pk = package_need(ctx, sc_id, need_id)
    hits = [x for x in pk["statements"] if x.get("id") == stmt_id]
    if not hits:
        if required:
            stop(f"{ctx.package_path[sc_id]}: no sentence {stmt_id} for {need_id}")
        return None, None
    if len(hits) > 1:
        stop(f"{ctx.package_path[sc_id]}: {len(hits)} sentences {stmt_id} for {need_id}; cannot cite one")
    text = hits[0]["text"]
    src = f"{ctx.package_path[sc_id]}#{need_id}/{stmt_id}"
    if resmod.resolve(src)["text"] != text:
        stop(f"{src} does not resolve to the sentence used")
    return text, src


def full_stop(text):
    return text if text.rstrip().endswith((".", "!", "?")) else text.rstrip() + "."


# ====================================================================== shared clause builders

def by_inv_text(ctx, ids):
    c = Counter(ctx.test[t]["investigation_id"] for t in ids)
    items = sorted(c.items(), key=lambda kv: (-kv[1], acc_key(kv[0])))
    return ", ".join(f"{ctx.name(a)} {n}" for a, n in items), dict(items)


def by_kind_text(ctx, ids):
    c = Counter((ctx.test[t]["investigation_id"], ctx.test[t]["fuel_phase"], ctx.test[t]["sample_geometry"]) for t in ids)
    items = sorted(c.items(), key=lambda kv: (-kv[1], acc_key(kv[0][0])))
    parts, facts = [], {}
    for (acc, ph, geo), n in items:
        parts.append(f"{n} {T.kind_noun(ph, geo, n)} from {ctx.name(acc)}")
        facts[f"{acc} {ph} {geo or 'geometry not recorded'}"] = n
    return "; ".join(parts), facts


def missing_clause(ctx, ids, var):
    """Why `var` is absent for these tests: not a column (per table) or empty cells. Returns (text|None, facts, sources)."""
    by_src = defaultdict(list)
    for t in ids:
        if not ctx.test[t][var]:
            by_src[ctx.test[t]["source_id"]].append(t)
    if not by_src:
        return None, {}, []
    no_col = sorted([s for s in by_src if var not in ctx.source_vars(s)], key=lambda s: (acc_key(ctx.source[s]["investigation_id"]), s))
    with_col = sorted([s for s in by_src if var in ctx.source_vars(s)], key=lambda s: (acc_key(ctx.source[s]["investigation_id"]), s))
    # review: a test whose value the pipeline flagged and left out has a cell that is not empty
    flagged = {s: [t for t in by_src[s] if flag_of(ctx.test[t], var)] for s in with_col}
    flagged = {s: ts for s, ts in flagged.items() if ts}
    empty = [s for s in with_col if len(flagged.get(s, [])) < len(by_src[s])]
    parts, facts, sources = [], {}, []
    if no_col:
        txt = T.not_a_column(var, [ctx.table_name(s) for s in no_col])
        facts[f"{var}_not_a_column_tests"] = sum(len(by_src[s]) for s in no_col)
        if var == "pressure_kpa":
            said = []
            for s in no_col:
                acc = ctx.source[s]["investigation_id"]
                for u in evmod.units(acc, ev=ctx.ev):
                    if MEASURED_PRESSURE.search(u["text"]):
                        said.append((acc, u))
                        break
            if said:
                txt += f" ({T.measured_not_in_table([a for a, _ in said])})"
                facts["pressure_measured_per_record"] = {a: u["id"] for a, u in said}
                sources += [u["source"] for _, u in said]
        parts.append(txt)
        sources += [f"{F_SOURCES}#{s}" for s in no_col]
    if empty:
        k = sum(len(by_src[s]) - len(flagged.get(s, [])) for s in empty)
        parts.append(T.cell_empty(var, k, [ctx.table_name(s) for s in empty]))
        facts[f"{var}_empty_cells"] = k
        sources += [f"{F_SOURCES}#{s}" for s in empty]
    for sid, ts in flagged.items():
        flags = unique(flag_of(ctx.test[t], var) for t in ts)
        if len(flags) != 1:
            stop(f"{sid}: {var} cells flagged for more than one reason {flags}; no wording for that")
        column, cells = raw_cells(ctx, sid, var, ts)
        parts.append(T.cell_not_used(var, len(ts), [ctx.table_name(sid)], cells, column, flags[0]))
        facts[f"{var}_flagged_not_used"] = len(ts)
        facts[f"{var}_flag"] = flags[0]
        if cells:
            facts[f"{var}_cells_as_written"] = cells
            nums = [fnum(c) for c in cells]
            if all(n is not None for n in nums):
                facts[f"{var}_cells_as_numbers"] = [int(n) if n.is_integer() else n for n in nums]
        sources += [f"{F_SOURCES}#{sid}"] + [f"{F_TESTS}#{t}" for t in ts[:3]]
    return "; ".join(parts), facts, sources


def flag_of(row, var):
    """The pipeline's reason for leaving `var` empty in this tests.csv row ('' when there is none)."""
    for f in (row.get("flags") or "").split(";"):
        if f.startswith(var + ":"):
            return f.split(":", 1)[1]
    return ""


def raw_cells(ctx, sid, var, test_ids):
    """The NASA cells behind `var` for these tests, read back from the PSI table through the column
    mapping in sources.json and the row number in tests.csv. Returns (column name, distinct cell texts),
    or (None, None) when the column or a row cannot be found; nothing is guessed."""
    src = ctx.source[sid]
    col = next((c["from"] for c in src.get("columns", []) if c["to"] == var), None)
    if col is None:
        return None, None
    with open(ROOT / TABLE_DIR / src["file"], newline="", encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.reader(f))
    if not rows:
        return None, None
    norm = lambda x: ws(x or "")  # noqa: E731
    idx = [i for i, h in enumerate(rows[0]) if norm(h) == norm(col)]
    if len(idx) != 1:
        return None, None
    cells = []
    for t in test_ids:
        r = int(ctx.test[t]["source_row"]) - 1
        if not (0 < r < len(rows)) or idx[0] >= len(rows[r]):
            return None, None
        cells.append(rows[r][idx[0]].strip())
    if any(c == "" for c in cells):
        return None, None  # an empty cell is not 'a value the pipeline does not use'
    return norm(col), unique(cells)


def balance_clause(ctx, ids):
    cats = defaultdict(list)
    co2_n = he_n = both_n = 0
    for t in ids:
        row = ctx.test[t]
        v = ctx.source_vars(row["source_id"])
        has_c, has_h = "co2_pct" in v, "he_pct" in v
        c, h = fnum(row["co2_pct"]), fnum(row["he_pct"])
        if not has_c and not has_h:
            cats["no_column"].append(t)
        elif (c or 0) > 0 or (h or 0) > 0:
            cats["diluted"].append(t)
            co2_n += (c or 0) > 0
            he_n += (h or 0) > 0
            both_n += (c or 0) > 0 and (h or 0) > 0
        elif not (has_c and has_h):
            cats["one_column"].append(t)
        elif c == 0 and h == 0:
            cats["zero"].append(t)
        else:
            cats["empty"].append(t)
    n = len(ids)
    parts = []
    if cats["diluted"]:
        parts.append(T.balance_diluted(len(cats["diluted"]), co2_n, he_n, both_n, len(cats["zero"]), n))
    elif cats["zero"]:
        parts.append(T.balance_zero(len(cats["zero"]), n))
    if cats["no_column"]:
        srcs = sorted({ctx.test[t]["source_id"] for t in cats["no_column"]},
                      key=lambda s: (acc_key(ctx.source[s]["investigation_id"]), s))
        measured = [ctx.table_name(s) for s in srcs if "co2_initial_pct" in ctx.source_vars(s)]
        parts.append(T.balance_no_column(len(cats["no_column"]), [ctx.table_name(s) for s in srcs], measured))
    if cats["one_column"]:
        srcs = sorted({ctx.test[t]["source_id"] for t in cats["one_column"]})
        parts.append(T.balance_one_column(len(cats["one_column"]), [ctx.table_name(s) for s in srcs]))
    if cats["empty"]:
        parts.append(T.balance_empty(len(cats["empty"])))
    facts = {"balance_diluted": len(cats["diluted"]), "balance_co2_added": co2_n, "balance_he_added": he_n,
             "balance_both_added": both_n, "balance_zero": len(cats["zero"]),
             "balance_not_a_column": len(cats["no_column"]), "balance_one_column": len(cats["one_column"]),
             "balance_empty": len(cats["empty"])}
    facts = {k: v for k, v in facts.items() if v}
    if not parts:
        return None, facts
    return T.cap("; ".join(parts)) + ".", facts


def test_end_clause(ctx, ids):
    tally = Counter()
    for t in ids:
        row = ctx.test[t]
        if row["test_end"]:
            tally[row["test_end"]] += 1
        elif row["flow_event"]:
            tally["flow event " + row["flow_event"].replace("_", " ")] += 1
        else:
            tally["no recorded end"] += 1
    items = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))
    none_ext = not any("extinction" in k for k in tally)
    s = T.test_end_clause(len(ids), [(k, v) for k, v in items], none_ext)
    for k, note in T.TEST_END_NOTES.items():
        if k in tally:
            s += " " + note
    return s, {"test_end_" + k.replace(" ", "_"): v for k, v in items}


# ====================================================================== the challenge-statement bound

def _ref_parent(item_id):
    """The references.json entry (paper, standard, ...) that holds this item, or {}."""
    for r in _json(F_REFS)["references"]:
        if any(it["id"] == item_id for it in r.get("items", [])):
            return r
    return {}


def challenge_bound(ctx, sc_id):
    """reader (coord/decisions.md 14:15, data role's request 1328): the lunar-habitat scenario counts with a
    pressure bin that reaches above the 10.2 psi of the challenge statement, so every place that shows the
    matched count says where those tests were recorded. Returns None when the scenario does not rest on the
    challenge-statement item or its pressure bin does not reach above it. Everything is computed here from
    tests.csv, need_tests.csv and scenario_tests.csv; nothing is typed in:
      - the bound: CH.moonbase values (oxygen minimum, pressure maximum in psi), converted to kPa;
      - below: counted tests (objective link 'stated', any need) with ambient oxygen at or above the
        minimum and a recorded pressure at or below the bound;
      - inside: counted tests whose oxygen and pressure are inside the team bins (tier 'atmosphere').
    Pressures are shown to 0.1 kPa when the data role's scenario note states the same rounded value (the
    note is then the cited source of the rounded number); otherwise as written in tests.csv. 'About N atm'
    is printed only when the note itself gives a pressure in atm with that value."""
    if sc_id in ctx._bound:
        return ctx._bound[sc_id]
    ctx._bound[sc_id] = None
    sc = ctx.scen[sc_id]
    it = ctx.refs.get(CHALLENGE_ITEM)
    vals = (it or {}).get("values") or {}
    psi, o2_min = vals.get("pressure_psia_max"), vals.get("o2_pct_min")
    pr = (sc.get("ranges") or {}).get("pressure_kpa") or {}
    if (CHALLENGE_ITEM not in (sc.get("basis") or []) or psi is None or o2_min is None
            or pr.get("max") is None):
        return None
    exact = psi * KPA_PER_PSI
    if pr["max"] <= exact:
        return None
    counted = sorted({r["test_id"] for r in ctx.need_tests if r["objective_link"] == "stated"})

    def val(t, var):
        return fnum(ctx.test[t][var])

    def at_or_below(t):
        return (ctx.test[t]["o2_basis"] == "ambient" and val(t, "o2_pct") is not None and val(t, "o2_pct") >= o2_min
                and val(t, "pressure_kpa") is not None and val(t, "pressure_kpa") <= exact)
    below = [t for t in counted if at_or_below(t)]
    # reader 2: 'no counted test' is not 'no test'. Tests that are counted for no need and were recorded at or
    # below the bound (PSI-159 gas-burner flames) are named in the frame, per investigation.
    counted_set = set(counted)
    uncounted_below = defaultdict(list)
    for t in ctx.tests:
        if t["test_id"] not in counted_set and at_or_below(t["test_id"]):
            uncounted_below[t["investigation_id"]].append(t["test_id"])
    marks = ctx.scen_tests[sc_id]
    inside = [t for t in counted if marks[t]["tier"] == "atmosphere"]
    # the data role's note on the scenario (pipeline/spec/scenarios.json), cited by its key path; a source
    # under data/pipeline/evidence/ would have to be quoted in full (ai/check_all.py), and the note is long
    note = sc.get("note") or ""
    order = [x["id"] for x in _json(F_SCENARIOS)["scenarios"]]
    note_src = f"{F_SCENARIOS}#scenarios.{order.index(sc_id)}.note"
    if not note or not resmod.check(note_src) or resmod.resolve(note_src)["text"] != note:
        note, note_src = "", None
    note_nums = {float(x) for x in re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", note)}
    text = (it or {}).get("text") or ""
    caveat, caveat_src = scenario_caveat(ctx, sc_id)
    b = {"psi": psi, "o2_min": o2_min, "kpa": round(exact, 1), "exact": exact, "item_text": text,
         "below": below, "inside": inside, "note_nums": note_nums, "note_src": note_src,
         "caveat": caveat, "caveat_src": caveat_src, "counted": counted_set,
         "uncounted_below": {acc: sorted(ids) for acc, ids in sorted(uncounted_below.items(), key=lambda kv: acc_key(kv[0]))},
         "atm_in_note": bool(re.search(r"\b\d+(?:\.\d+)? atm\b", note))}
    ctx._bound[sc_id] = b
    return b


def scenario_caveat(ctx, sc_id):
    """The data role's caveat on a scenario (evidence package, environment.caveat) and its source string, or
    (None, None). 14:59 merge: it is used as written and cited (contracts/README.md: the scenario caveat is cited
    by its key path). reader 2: every scenario that has one shows it, not only lunar_habitat."""
    pk = ctx.package.get(sc_id) or {}
    caveat = ((pk.get("environment") or {}).get("caveat") or "").strip()
    if not caveat:
        return None, None
    src = f"{ctx.package_path[sc_id]}#environment.caveat"
    if resmod.resolve(src)["text"] != caveat:
        stop(f"{src} does not resolve to the caveat used")
    return caveat, src


def package_ranges(ctx, sc_id, ids):
    """The data role's matched ranges (evidence package, needs[i].matched_ranges) of the need block whose
    matched tests are exactly these tests, with its source string; (None, None) when no block matches."""
    pk = ctx.package.get(sc_id) or {}
    want = set(ids)
    for i, n in enumerate(pk.get("needs") or []):
        if {m["test_id"] for m in n.get("matched_tests") or []} == want and n.get("matched_ranges"):
            src = f"{ctx.package_path[sc_id]}#needs.{i}.matched_ranges"
            if resmod.resolve(src)["data"]["value"] != n["matched_ranges"]:
                stop(f"{src} does not resolve to the matched ranges used")
            return n["matched_ranges"], src
    return None, None


def bound_span(ctx, b, ids, sc_id=None):
    """Recorded oxygen and pressure of these tests against the challenge-statement bound: the values as
    shown, the tests.csv rows they come from, the facts and the sources. None when a value is missing.
    coord/decisions.md 14:15: the pressures are shown as whole kPa ('about 0.7 atm (71 to 72 kPa)'); where the
    data role's evidence package has a need block with exactly these matched tests, its matched_ranges must
    equal the values recounted here from tests.csv, and it is cited."""
    rows = [(t, fnum(ctx.test[t]["o2_pct"]), fnum(ctx.test[t]["pressure_kpa"])) for t in ids]
    if not rows or any(o is None or p is None for _, o, p in rows):
        return None
    o_lo, o_hi = min(rows, key=lambda r: (r[1], r[0])), max(rows, key=lambda r: (r[1], r[0]))
    p_lo, p_hi = min(rows, key=lambda r: (r[2], r[0])), max(rows, key=lambda r: (r[2], r[0]))
    mr, mr_src = package_ranges(ctx, sc_id, ids) if sc_id else (None, None)
    if mr is not None:
        po, pp = mr.get("o2_pct") or {}, mr.get("pressure_kpa") or {}
        if (po.get("recorded"), pp.get("recorded")) != (len(rows), len(rows)) or \
                (po.get("min"), po.get("max"), pp.get("min"), pp.get("max")) != (o_lo[1], o_hi[1], p_lo[2], p_hi[2]):
            stop(f"{mr_src} differs from the recount of the matched tests from tests.csv")
    kpa = (int(round(p_lo[2])), int(round(p_hi[2])))
    atm = {round(p_lo[2] / KPA_PER_ATM, 1), round(p_hi[2] / KPA_PER_ATM, 1)}
    atm = atm.pop() if len(atm) == 1 and b["atm_in_note"] and next(iter(atm)) in b["note_nums"] else None
    above = None
    if p_lo[2] > b["exact"]:
        above = (int(round(p_lo[2] - b["exact"])), int(round(p_hi[2] - b["exact"])))
        if above[0] < 1:
            above = None  # less than half a kPa above: no 'N kPa above' wording
    cited = unique([o_lo[0], o_hi[0], p_lo[0], p_hi[0]])
    facts = {"challenge_bound": {"o2_pct_min": b["o2_min"], "pressure_psi_max": b["psi"], "pressure_kpa": b["kpa"],
                                 "psi_to_kpa": KPA_PER_PSI},
             "tests_with_these_values": len(rows),
             "recorded_o2_pct": {"min": o_lo[1], "max": o_hi[1]},
             "recorded_pressure_kpa_rounded": {"min": kpa[0], "max": kpa[1]},
             "recorded_pressure_kpa_in_tests_csv": {p_lo[0]: p_lo[2], p_hi[0]: p_hi[2]},
             "counted_tests_at_or_below_challenge_bound": len(b["below"])}
    # reader 2: an oxygen value with decimals (PSI-159: 33.2446%, from a mole fraction in the NASA table) is shown as
    # a whole percent, like the pressures; the values as written in tests.csv stay in the facts
    o2 = (o_lo[1], o_hi[1])
    if not all(float(v).is_integer() for v in o2):
        o2 = (int(round(o_lo[1])), int(round(o_hi[1])))
        facts["recorded_o2_pct_rounded"] = {"min": o2[0], "max": o2[1]}
    if atm is not None:
        facts["recorded_pressure_atm_rounded"] = atm
    if above:
        facts["kpa_above_challenge_bound_rounded"] = list(above)
    sources = [f"{F_REFS}#{CHALLENGE_ITEM}"] + ([b["note_src"]] if b["note_src"] else []) \
        + ([mr_src] if mr_src else []) + [f"{F_TESTS}#{t}" for t in cited]
    return {"o2": o2, "kpa": kpa, "atm": atm, "above": above, "facts": facts, "sources": sources,
            "all_above": p_lo[2] > b["exact"], "all_at_or_below": p_hi[2] <= b["exact"]}



# ====================================================================== need statements

def need_entry(ctx, sc_id, need):
    rc = recount(ctx, sc_id, need["id"])
    sc = ctx.scen[sc_id]
    st, u, tiers = rc["status"], len(rc["usable"]), rc["tiers"]
    nid = need["id"]
    facts = {"usable_tests": u}
    if sc["ranges"]:
        facts["team_bins"] = bins_facts(sc["ranges"])  # review: the bin limits are printed, so they are facts
    sources = [f"{F_SCEN_NEEDS}#{sc_id}/{nid}", f"{F_SCENARIOS}#{sc_id}"]
    rules = [f"status:{st}"]
    parts = [T.lead(sc["ranges"])]
    counted = []

    missing_said = []  # (variable, source ids) of every 'not a column / empty cell' clause in the statement

    def add_missing(ids, var):
        txt, f, s = missing_clause(ctx, ids, var)
        facts.update(f)
        sources.extend(s)
        if txt:
            missing_said.append((var, {ctx.test[t]["source_id"] for t in ids if not ctx.test[t][var]}))
        return txt

    def add_pipe(stmt_id, required=True):
        """Append the pipeline's fixed sentence and cite it; returns its text or None."""
        text, src = pipe_sentence(ctx, sc_id, nid, stmt_id, required=required)
        if text is None:
            return None
        parts.append(full_stop(text))
        sources.append(src)
        rules.append(f"pipeline:{stmt_id}")
        return text

    if st not in T.STATUS_PIPELINE_SENTENCE:  # recount() already stops on this
        stop(f"no template for status {st!r}")
    # (1) the status, as the pipeline words it (review 14 Nov: the same statement in both places)
    add_pipe(T.STATUS_PIPELINE_SENTENCE[st])
    def by_inv_clause(txt, f, n):
        # reader: the clause names the tests it breaks down (see templates.by_investigation)
        return T.by_investigation(txt, n, ctx.name(next(iter(f))) if len(f) == 1 else None)

    if st == "in_atmosphere":
        counted = tiers["atmosphere"]
        txt, f = by_inv_text(ctx, counted)
        parts.append(by_inv_clause(txt, f, len(counted)))
        facts.update(tests_atmosphere=len(counted), atmosphere_by_investigation=f)
        # reader (decision 14:15): where the pressure bin reaches above the challenge-statement pressure,
        # the recorded oxygen and pressure of the matched tests go right next to their count
        b = challenge_bound(ctx, sc_id)
        span = bound_span(ctx, b, counted, sc_id) if b else None
        if span:
            parts.append(T.matched_bound_clause(len(counted), span["o2"], span["kpa"], span["atm"], span["above"],
                                                b["psi"], b["kpa"], b["o2_min"], len(b["below"])))
            facts.update(span["facts"])
            sources.extend(span["sources"])
            rules.append("clause:challenge_bound")
        oxy = tiers["oxygen_only"]
        if oxy:
            txt, f = by_inv_text(ctx, oxy)
            parts.append(T.further_oxygen_only(len(oxy), txt, add_missing(oxy, "pressure_kpa")))
            facts.update(tests_oxygen_only=len(oxy), oxygen_only_by_investigation=f)
            rules.append("clause:further_oxygen_only")
        pres = tiers["pressure_only"]
        if pres:
            txt, f = by_inv_text(ctx, pres)
            parts.append(T.further_pressure_only(len(pres), txt))
            facts.update(tests_pressure_only=len(pres), pressure_only_by_investigation=f)
            rules.append("clause:further_pressure_only")
    elif st == "oxygen_only":
        counted = tiers["oxygen_only"]
        txt, f = by_inv_text(ctx, counted)
        p = add_missing(counted, "pressure_kpa")
        if not p:
            stop(f"{sc_id}/{nid}: oxygen_only tests with a pressure value")
        parts.append(by_inv_clause(txt, f, len(counted)))
        parts.append(T.cap(p) + ".")
        facts.update(tests_oxygen_only=len(counted), oxygen_only_by_investigation=f)
    elif st == "pressure_only":
        counted = tiers["pressure_only"]
        txt, f = by_inv_text(ctx, counted)
        o = add_missing(counted, "o2_pct")
        if not o:
            stop(f"{sc_id}/{nid}: pressure_only tests with an oxygen value")
        parts.append(by_inv_clause(txt, f, len(counted)))
        parts.append(T.cap(o) + ".")
        facts.update(tests_pressure_only=len(counted), pressure_only_by_investigation=f)
    elif st == "not_measured":
        facts["investigations_in_psi"] = ctx.n_investigations
        sources.append(f"{F_NEEDS}#{nid}")
    elif st == "other_atmosphere":
        facts["ranges_compared"] = 2  # the pipeline sentence's 'one of the two ranges' (oxygen, pressure)

    # (a) basis of the usable set
    stream = [t for t in rc["usable"] if ctx.test[t]["o2_basis"] == "oxidizer_stream"]
    if stream:
        amb = sum(ctx.test[t]["o2_basis"] == "ambient" for t in rc["usable"])
        parts.append(T.basis_clause(u, amb, len(stream)))
        facts.update(usable_ambient=amb, usable_oxidizer_stream=len(stream))
        rules.append("clause:basis")
    # (b) phase and (c) balance gas of the tests counted inside the bins
    if counted:
        kinds = {(ctx.test[t]["fuel_phase"], ctx.test[t]["sample_geometry"]) for t in counted}
        phases = {k[0] for k in kinds}
        if len(kinds) == 1 or phases == {"solid"}:
            ph, geo = sorted(kinds)[0]
            noun = T.kind_noun(ph, geo if len(kinds) == 1 else None, len(counted))
            parts.append(T.phase_clause(len(counted), noun, ph == "solid"))
            rules.append("clause:phase")
        b, bf = balance_clause(ctx, counted)
        check_added_gas(ctx, sc_id, nid, rc, counted, bf)
        if b:
            parts.append(b)
            facts.update(bf)
            rules.append("clause:balance_gas")
        # (d) test ends, for the extinction need
        if nid == "S1":
            e, ef = test_end_clause(ctx, counted)
            parts.append(e)
            facts.update(ef)
            rules.append("clause:test_end")
    # flow, where the scenario sets a flow range: the pipeline's comparison of the matched tests
    matched = tiers["atmosphere"] + tiers["oxygen_only"]
    if sc["ranges"].get("flow_cms") and matched:
        if add_pipe("flow.compared"):
            c = rc["package"]["counts"]
            facts.update(matched_tests=len(matched), matched_flow_in_range=c["matched_flow_in_range"],
                         matched_flow_not_recorded=c["matched_flow_not_recorded"])
            # reader: the pipeline sentence gives the tests inside the flow range and those with no flow
            # value; the rest are the tests recorded outside it (scenario_tests.csv flow_match 'out')
            fm = Counter(ctx.scen_tests[sc_id][t]["flow_match"] for t in matched)
            if (fm.get("in", 0), fm.get("not_recorded", 0)) != (c["matched_flow_in_range"], c["matched_flow_not_recorded"]) \
                    or set(fm) - {"in", "out", "not_recorded"}:
                stop(f"{sc_id}/{nid}: flow_match of the matched tests {dict(fm)} differs from the package counts")
            if fm.get("out"):
                parts.append(T.flow_outside(fm["out"]))
                facts["matched_flow_outside_range"] = fm["out"]
                rules.append("clause:flow_outside")
    # (f) gap sentences
    for code in rc["gaps"]:
        if code in ("pressure:not_recorded", "oxygen:not_recorded"):
            var = "pressure_kpa" if code.startswith("pressure") else "o2_pct"
            if st in ("oxygen_only", "pressure_only") and var == ("pressure_kpa" if st == "oxygen_only" else "o2_pct"):
                rules.append(f"gap:{code}")
                continue  # already said after the status sentence
            txt = add_missing(rc["usable"], var)
            if not txt:
                stop(f"{sc_id}/{nid}: gap {code} but every usable test has {var}")
            parts.append(T.cap(txt) + ".")
        elif code in T.GAP_PIPELINE_SENTENCE:
            add_pipe(T.GAP_PIPELINE_SENTENCE[code])
            if code.startswith("flow:"):
                facts.setdefault("matched_tests", len(matched))
        elif code == "need:no_usable_test":
            if st != "not_measured":
                stop(f"{sc_id}/{nid}: need:no_usable_test with status {st}")
        else:  # recount() already stops on an unknown code
            stop(f"no wording for gap code {code!r}")
        rules.append(f"gap:{code}")
    # (f2) what a NASA record or a paper of the investigators says about a variable the table does not hold:
    # the data role's fixed 'documented.elsewhere' sentences (pipeline README: carried next to the gap, never used
    # as a value), placed after the clause that names the missing variable for that table, used as written
    for stmt_src, text, var, sid, said_in in documented_elsewhere(ctx, sc_id, nid):
        if any(v == var and sid in sids for v, sids in missing_said):
            parts.append(full_stop(text))
            sources.append(stmt_src)
            if said_in and f"{F_REFS}#{said_in}" not in sources and resmod.check(f"{F_REFS}#{said_in}"):
                sources.append(f"{F_REFS}#{said_in}")
            nums = re.findall(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w])", text)
            if nums:
                facts.setdefault("documented_elsewhere_numerals_as_written", [])
                facts["documented_elsewhere_numerals_as_written"] += [float(x) if "." in x else int(x) for x in nums]
            rules.append(f"pipeline:documented.elsewhere:{sid}")
    # (e) recorded outside the stated objective
    if rc["outside"]:
        ids = sorted({ctx.test[t]["investigation_id"] for t in rc["outside"]}, key=acc_key)
        # review: these tests are not counted, but the sentence must not let burner-stream oxygen
        # pass as an atmosphere (139 of the 272 PSI-159 tests outside S1 are inverse flames)
        stream_out = any(ctx.test[t]["o2_basis"] == "oxidizer_stream" for t in rc["outside"])
        # reader 2: an investigation whose PSI record names the objective but whose link the literature check marks
        # 'differs' or 'topic_only' is said as that, with the publication item; 'does not state this need as an
        # objective' contradicted the record (PSI-98 for P1, PSI-99 for P3: the shared Saffire objective sentence)
        unsupported = {"differs": [], "topic_only": []}
        verdicts = {}
        for acc in ids:
            rows = [r for r in ctx.obj_links_all if r["need_id"] == nid and r["investigation_id"] == acc]
            if any((r.get("verdict") or "supported") == "supported" for r in rows):
                stop(f"{sc_id}/{nid}: tests of {acc} are outside the stated objective but objective_links.csv has "
                     "a supported link for them")
            for verdict in unsupported:
                hit = [r for r in rows if r.get("verdict") == verdict and (r.get("record_field") or "").strip()]
                if not hit:
                    continue
                items = unique(r["publication_item"].strip() for r in hit if (r.get("publication_item") or "").strip())
                unsupported[verdict].append((acc, items))
                verdicts[acc] = verdict
                sources.append(f"{F_OBJ_LINKS}#{nid}/{acc}")
                sources.extend(f"{acc}.{r['record_field'].strip()}" for r in hit)
                sources.extend(f"{F_REFS}#{i}" for i in items)
                break
        parts.append(T.outside_objective(len(rc["outside"]), ids, stream_out, further=u > 0,
                                         differs=unsupported["differs"], topic_only=unsupported["topic_only"]))
        facts.update(tests_recorded_outside_objective=len(rc["outside"]), outside_objective_investigations=ids)
        if verdicts:
            facts["outside_objective_link_verdicts"] = verdicts
        if stream_out:
            facts["outside_objective_includes_inverse_flames"] = True
            rules.append("clause:outside_objective_inverse_flames")
        sources.append(f"{F_NEED_TESTS}#{nid}")
        rules.append("clause:outside_objective")
    # (g) what a count of this need means: the need's reading (pipeline/spec/needs.json), as the
    # evidence package words it
    reading, rsrc = pipe_sentence(ctx, sc_id, nid, "need.reading")
    if ws(reading) != ws(need.get("reading") or ""):
        stop(f"{rsrc} is not the reading of {nid} in pipeline/spec/needs.json")
    parts.append(T.READING_LEAD + full_stop(reading))
    # the reading is the data role's text and is used as written; where it says that no test is counted while
    # the count is not zero (D1 after the literature check of commit a5a9e87), the build says so loudly
    if u > 0 and READING_SAYS_NONE.search(reading):
        msg = (f"{sc_id}/{nid}: the pipeline's reading says no test is counted, but {u} tests are counted "
               f"({rsrc}; pipeline/spec/needs.json); a request to the data role, not fixed here")
        if msg not in ctx.warnings:
            ctx.warnings.append(msg)
        # reader 2: the reading is not changed, but the statement must not contradict itself without a word: a
        # team note says which of the two is current and, where every counted test rests on a publication only,
        # through which item (D1: BASS2TM.products). The note goes away when the reading no longer says so.
        accs = sorted({ctx.test[t]["investigation_id"] for t in rc["usable"]}, key=acc_key)
        own = [r for r in ctx.obj_links if r["need_id"] == nid and r["investigation_id"] in accs]
        pub_only = bool(own) and all(not (r.get("record_field") or "").strip()
                                     and (r.get("publication_item") or "").strip() for r in own)
        items = unique(r["publication_item"].strip() for r in own) if pub_only else []
        parts.append(T.reading_mismatch(u, [ctx.name(a) for a in accs] if pub_only else [], items))
        rules.append("clause:reading_mismatch")
    sources.append(rsrc)
    rules.append("pipeline:need.reading")
    # the stated objectives behind the counted tests
    for acc in sorted({ctx.test[t]["investigation_id"] for t in rc["usable"]}, key=acc_key):
        links = [r for r in ctx.obj_links if r["need_id"] == nid and r["investigation_id"] == acc]
        if not links:
            stop(f"{sc_id}/{nid}: tests of {acc} are counted but objective_links.csv has no supported link for them")
        for r in links:
            sources += ctx.link_sources(r)
    return {"need_id": nid, "need": need["name"], "statement": " ".join(parts), "sources": unique(sources),
            "status": st, "facts": facts, "text_origin": "template", "rule": rules}


def documented_elsewhere(ctx, sc_id, nid):
    """[(source, text, variable, source_id, said_in)] for the 'documented.elsewhere' sentences of this need in the
    scenario's evidence package. The sentences share one id, so each is cited by its key path
    (needs.<i>.statements.<j>), which must resolve to the same text."""
    pk = ctx.package.get(sc_id) or {}
    out = []
    for i, n in enumerate(pk.get("needs") or []):
        if n.get("need_id") != nid:
            continue
        said = {(d.get("source_id"), d.get("variable")): d.get("said_in") for d in n.get("documented_elsewhere") or []}
        for j, st in enumerate(n.get("statements") or []):
            if st.get("id") != "documented.elsewhere":
                continue
            src = f"{ctx.package_path[sc_id]}#needs.{i}.statements.{j}"
            if resmod.resolve(src)["text"] != st["text"]:
                stop(f"{src} does not resolve to the sentence used")
            out.append((src, st["text"], st.get("variable"), st.get("source_id"),
                        said.get((st.get("source_id"), st.get("variable")))))
    return out


def check_added_gas(ctx, sc_id, nid, rc, counted, bf):
    """The pipeline's added_gas mark of the counted tests must agree with the team's balance-gas count."""
    marks = Counter(rc["matched"][t]["added_gas"] for t in counted)
    team = {"co2_or_helium": bf.get("balance_diluted", 0), "none": bf.get("balance_zero", 0)}
    team["not_recorded"] = len(counted) - team["co2_or_helium"] - team["none"]
    if {k: marks.get(k, 0) for k in team} != team or set(marks) - set(team):
        stop(f"{sc_id}/{nid}: the pipeline's added_gas marks {dict(marks)} differ from the team count {team}")


def bins_facts(ranges):
    """The scenario's bin limits as facts: {'o2_pct': {'min': 30, 'max': 36}, 'pressure_kpa': {'max': 85.8}}."""
    return {var: {k: r[k] for k in ("min", "max") if r.get(k) is not None} for var, r in ranges.items()
            if var in ("o2_pct", "pressure_kpa", "flow_cms") and r}


# ====================================================================== global facts

def global_facts(ctx):
    solid = [t for t in ctx.tests if t["fuel_phase"] == "solid"]
    solid_o2 = [(fnum(t["o2_pct"]), t["test_id"]) for t in solid if fnum(t["o2_pct"]) is not None]
    amb = [(fnum(t["o2_pct"]), t["test_id"]) for t in ctx.tests if t["o2_basis"] == "ambient" and fnum(t["o2_pct"]) is not None]
    strm = [(fnum(t["o2_pct"]), t["test_id"]) for t in ctx.tests if t["o2_basis"] == "oxidizer_stream" and fnum(t["o2_pct"]) is not None]
    solid_sources = sorted({t["source_id"] for t in solid})
    g = {
        "solid_tests": len(solid),
        "solid_tests_with_pressure": sum(1 for t in solid if t["pressure_kpa"]),
        "solid_sources": solid_sources,
        "solid_sources_with_pressure_column": [s for s in solid_sources if "pressure_kpa" in ctx.source_vars(s)],
        "solid_sources_without_o2_column": sorted(
            [s for s in solid_sources if "o2_pct" not in ctx.source_vars(s)],
            key=lambda s: (acc_key(ctx.source[s]["investigation_id"]), s)),
        "max_solid_o2": max(solid_o2), "max_ambient_o2": max(amb), "max_stream_o2": max(strm),
    }
    return g


def psi20_table(ctx):
    """Day count, flames ignited and oxygen settings of the PSI-20 test-day table, read from the NASA file."""
    src = next((s for s in ctx.sources_of.get("PSI-20", []) if s["row_unit"] == "test_day"), None)
    if src is None:
        return None
    return test_day_table(ctx, src)


def test_day_table(ctx, src):
    with open(ROOT / TABLE_DIR / src["file"], newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]
    out = {"source_id": src["id"], "days": len(rows), "flames": None, "o2": None, "pressure_phrase": None,
           "o2_approximate_ignited": False}
    fcol = next((c for c in rows[0] if c and c.lower().rstrip("*").strip() == "flames ignited"), None) if rows else None
    if fcol:
        vals = [(r[fcol] or "").strip() for r in rows]
        if all(re.fullmatch(r"\d+", v) for v in vals):
            out["flames"] = sum(int(v) for v in vals)
    ocol = next((c for c in rows[0] if c and c.startswith("Oxygen Conc")), None) if rows else None
    if ocol:
        nums, as_written = [], []
        for r in rows:
            cell = (r[ocol] or "").strip()
            parts = [p.strip() for p in cell.split(";")]
            if all(re.fullmatch(r"\d+(\.\d+)?", p) for p in parts):
                nums += [float(p) for p in parts]
            else:
                as_written.append(cell)
        out["o2"] = {"min": min(nums), "max": max(nums), "as_written": as_written}
    ncol = next((c for c in rows[0] if c == "Notes"), None) if rows else None
    if ncol:
        for r in rows:
            m = re.search(r"not identified in this summary table", r[ncol] or "")
            if m and re.search(r"chamber pressures", r[ncol], re.I):
                out["pressure_phrase"] = m.group(0)
            # review: the notes say what the oxygen column holds; the wording follows them only if found
            if re.search(r"approximate concentrations for tests that ignited", r[ncol] or "", re.I):
                out["o2_approximate_ignited"] = True
    return out


def table_rows(src):
    with open(ROOT / TABLE_DIR / src["file"], newline="", encoding="utf-8-sig") as f:
        return sum(1 for r in csv.DictReader(f) if any((v or "").strip() for v in r.values()))


# ====================================================================== frames

def nasa_quote(ctx, item_id):
    """The 'quote' field of a references.json item (the sentence as written in the NASA document,
    kept by the data role), or None. The build never writes a quotation of its own."""
    q = (ctx.refs.get(item_id) or {}).get("quote")
    return ws(q) if q else None


def frame(ctx, sc_id, g):
    sc = ctx.scen[sc_id]
    label = sc["label"]
    parts = [T.frame_bins(label, sc["ranges"])]
    sources = [f"{F_SCENARIOS}#{sc_id}"]
    facts = {}
    # reader 2: who matched the purpose sentences to the needs is said while needs.json says it is not human-reviewed
    rule = T.frame_rule(T.NOT_HUMAN_REVIEWED in str(ctx.needs_doc["_meta"].get("generated_by", "")).lower())
    if sc["ranges"]:
        facts["team_bins"] = bins_facts(sc["ranges"])
        # reader (decision 14:15): the lunar-habitat frame says that the pressure bin is wider than the
        # challenge-statement pressure, that no counted test was recorded at or below it with the
        # challenge-statement oxygen, and where the counted tests inside the bins were recorded
        b = challenge_bound(ctx, sc_id)
        caveat, caveat_src = scenario_caveat(ctx, sc_id)
        if b:
            span = bound_span(ctx, b, b["inside"], sc_id) if b["inside"] else None
            inside = None
            if span:
                kinds = {(ctx.test[t]["fuel_phase"], ctx.test[t]["sample_geometry"]) for t in b["inside"]}
                noun = (T.kind_noun(*next(iter(kinds)), len(b["inside"])) if len(kinds) == 1
                        else T.plural(len(b["inside"]), "test"))
                inside = {"n": len(b["inside"]), "noun": noun, "o2": span["o2"], "kpa": span["kpa"],
                          "atm": span["atm"], "above": span["above"]}
                facts.update(span["facts"])
                facts["counted_tests_inside_bins"] = len(b["inside"])
                sources.extend(span["sources"])
            else:
                facts.update(challenge_bound={"o2_pct_min": b["o2_min"], "pressure_psi_max": b["psi"],
                                              "pressure_kpa": b["kpa"], "psi_to_kpa": KPA_PER_PSI},
                             counted_tests_at_or_below_challenge_bound=len(b["below"]))
                sources.append(f"{F_REFS}#{CHALLENGE_ITEM}")
            if not b["item_text"] or str(T.num(b["o2_min"])) not in b["item_text"] or str(T.num(b["psi"])) not in b["item_text"]:
                stop(f"{CHALLENGE_ITEM}: the item text no longer carries its values {b['o2_min']}% and {b['psi']} psi")
            # reader 2: tests counted for no need that were recorded at or below the bound, per investigation (no
            # count is printed in the frame; the result note of the investigation gives its tests inside the bins)
            uncounted = []
            for acc, ids in b["uncounted_below"].items():
                kinds = {(ctx.test[t]["fuel_phase"], ctx.test[t]["sample_geometry"]) for t in ids}
                noun = T.kind_noun(*next(iter(kinds)), 2) if len(kinds) == 1 else "tests"
                uncounted.append({"noun": noun, "inv": ctx.name(acc), "linked": bool(ctx.links_of(acc))})
                lo = min(ids, key=lambda t: (fnum(ctx.test[t]["o2_pct"]), t))
                hi = max(ids, key=lambda t: (fnum(ctx.test[t]["o2_pct"]), t))
                sources.extend(f"{F_TESTS}#{t}" for t in unique([lo, hi]))
            if uncounted:
                facts["investigations_with_uncounted_tests_at_or_below_challenge_bound"] = list(b["uncounted_below"])
            parts.append(T.frame_challenge_bound(b["item_text"], b["psi"], b["kpa"], b["o2_min"], len(b["below"]),
                                                 inside, caveat, uncounted))
            facts.setdefault("challenge_bound", {"o2_pct_min": b["o2_min"], "pressure_psi_max": b["psi"],
                                                 "pressure_kpa": b["kpa"], "psi_to_kpa": KPA_PER_PSI})
        elif caveat:
            parts.append(T.data_note(caveat))
        if caveat:
            sources.append(caveat_src)
            nums_caveat = re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])", caveat)
            if nums_caveat:
                facts["caveat_numerals_as_written"] = [float(x) if "." in x else int(x) for x in nums_caveat]
        parts += [rule, T.FRAME_STREAM]
    else:
        parts.append(rule)
    if sc.get("gravity_level") in ("lunar", "martian"):
        parts += [T.FRAME_GRAVITY, T.nasa_gravity_gap(nasa_quote(ctx, "TB008.gaps"))]
        sources.append(f"{F_REFS}#TB008.gaps")
        facts["tests_not_microgravity"] = 0
        # design A2 (1): the Olson and Ferkul Table I sentence goes into the frame, once per scenario
        drop = drop_test_comparison(ctx, sc["gravity_level"])
        if drop:
            parts.append(T.frame_drop_tests(sc["gravity_level"], **drop["wording"]))
            sources.append(f"{F_REFS}#OF2012.table1")
            facts.update(drop["facts"])
    if sc_id == "mars_habitat":
        item = ctx.refs["EAWG.atmospheres"]
        pairs = [(p, o) for p, o in item["values"]["atmospheres_psia_o2pct"] if o == 32]
        if not pairs or "surface habitats" not in item["text"]:
            stop("EAWG.atmospheres no longer lists the 32% surface-habitat atmospheres")
        kpa = [(p, f"{p * 6.894757:.1f}") for p, _ in pairs]
        parts.append(T.frame_mars(kpa))
        sources += [f"{F_REFS}#EAWG.atmospheres", f"{F_SCORING}#presets.mars_habitat"]
        facts["eawg_surface_atmospheres_psia_kpa_o2"] = [[p, float(k), 32] for p, k in kpa]
        facts["psia_to_kpa"] = 6.894757
    if sc_id == "spacesuit":
        (a, at), (s, st) = g["max_ambient_o2"], g["max_stream_o2"]
        parts.append(T.frame_spacesuit(a, s))
        sources += [f"{F_TESTS}#{at}", f"{F_TESTS}#{st}"]
        facts.update(max_ambient_o2=a, max_ambient_o2_test=at, max_stream_o2=s, max_stream_o2_test=st)
    parts.append(T.SCENARIO_LABEL)
    return " ".join(parts), unique(sources), facts


# ====================================================================== gaps

def gaps(ctx, sc_id, needs_out, recounts, g):
    sc = ctx.scen[sc_id]
    out = []
    gravity = sc.get("gravity_level")
    gravity_gap = gravity in ("lunar", "martian") and any(
        f"gravity:no_usable_test_at_{gravity}" in rc["gaps"] for rc in recounts.values())
    if gravity_gap:
        text = T.gap_gravity(gravity, nasa_quote(ctx, "TB008.gaps"))
        sources = [f"{F_REFS}#TB008.gaps", f"{F_SCEN_NEEDS}#{sc_id}"]
        facts = {"tests_in_psi_tables": len(ctx.tests), "tests_not_microgravity": 0}
        rule = f"gravity:no_usable_test_at_{gravity}"
        out.append({"text": text, "needed_data": T.gap_gravity_needed(gravity),
                    "sources": sources, "rule": rule, "status": "from_rule",
                    "facts": facts, "text_origin": "template"})
    # solid fuels at the scenario atmosphere
    solid_needs = [n["id"] for n in ctx.needs if (n.get("scope") or {}).get("fuel_phase") == ["solid"]]
    hit = [nid for nid in solid_needs if recounts[nid]["status"] in ("other_atmosphere", "oxygen_only")]
    if hit:
        if g["solid_tests_with_pressure"] or g["solid_sources_with_pressure_column"]:
            stop("a solid-sample test now has a pressure value: the solid gap wording no longer holds")
        mo2, mtest = g["max_solid_o2"]
        no_o2 = g["solid_sources_without_o2_column"]
        text = T.gap_solid(ctx.n_investigations, mo2, [ctx.table_name(s) for s in no_o2])
        facts = {"investigations_in_psi": ctx.n_investigations, "solid_tests": g["solid_tests"],
                 "solid_tests_with_pressure": 0, "max_solid_o2": mo2, "max_solid_o2_test": mtest,
                 "solid_tables_without_oxygen_column": no_o2, "needs": hit}
        sources = [f"{F_TESTS}#{mtest}"] + [f"{F_SOURCES}#{s}" for s in g["solid_sources"]]
        o2r = sc["ranges"].get("o2_pct") or {}
        p20 = psi20_table(ctx)
        if o2r.get("min") is not None and o2r["min"] > mo2 and p20 and p20["o2"] and p20["o2"]["max"] >= o2r["min"]:
            if not p20["o2_approximate_ignited"]:
                stop("the PSI-20 table notes no longer call its oxygen values approximate concentrations for "
                     "tests that ignited: the PSI-20 clause of the solid gap no longer holds")
            text += " " + T.gap_solid_psi20(p20["o2"]["max"], bool(p20["pressure_phrase"]))
            facts["psi20_max_o2_setting"] = p20["o2"]["max"]
            sources.append(f"{F_SOURCES}#acme_bre")
        saf = saffire_in_bins(ctx, sc)
        if saf:
            text += " " + T.gap_solid_saffire(saf["samples"], saf["n_samples"], ctx.n_investigations, saf["ai_read"],
                                              saf["paper_title"])
            sources.append(f"{F_REFS}#SAF456.conditions")
            facts.update(saffire_samples_inside_team_bins=[s for s, _, _ in saf["samples"]],
                         saffire_sample_conditions_o2_mol_pct_kpa=[[o, p] for _, o, p in saf["samples"]],
                         saffire_samples_in_table=saf["n_samples"], saffire_table_number=1,
                         saffire_flights_among_the_psi_investigations=[],
                         saffire_samples_counted=0)
        out.append({"text": text, "needed_data": T.GAP_SOLID_NEEDED, "sources": sources, "rule": "solid_at_atmosphere",
                    "status": "from_rule", "facts": facts, "text_origin": "template"})
    # phase of the tests inside the bins for S1
    if "S1" in recounts and recounts["S1"]["status"] == "in_atmosphere":
        ids = recounts["S1"]["tiers"]["atmosphere"]
        kinds = {(ctx.test[t]["fuel_phase"], ctx.test[t]["sample_geometry"]) for t in ids}
        if kinds == {("liquid", "droplet")}:
            invs = sorted({ctx.test[t]["investigation_id"] for t in ids}, key=acc_key)
            gfacts, gsrc, caveat = {"s1_tests_atmosphere": len(ids), "investigations": invs}, [f"{F_SCEN_NEEDS}#{sc_id}/S1"], None
            # reader (decision 14:15): the caveat goes wherever the count of matched tests is shown
            b = challenge_bound(ctx, sc_id)
            span = bound_span(ctx, b, ids, sc_id) if b else None
            if span and span["all_above"]:
                caveat = T.bound_short(span["o2"], span["kpa"], span["atm"], span["above"], b["psi"], b["kpa"])
                gfacts.update(span["facts"])
                gsrc += span["sources"]
            out.append({"text": T.gap_phase(len(ids), [ctx.name(a) for a in invs], caveat),
                        "needed_data": T.GAP_PHASE_NEEDED,
                        "sources": gsrc, "rule": "s1_phase_droplets_only",
                        "status": "from_rule", "facts": gfacts,
                        "text_origin": "template"})
    # detection
    # 14:59 merge: the detection gap was written for 'D2 counted, D1 not measured'; after the data role's
    # literature check D1 is counted (BASS-II, through BASS2TM.products) and D2 has none, and the old code dropped
    # the gap silently when D2 had no counted test. It is now built from both needs as they are.
    if "D2" in recounts and "D1" in recounts and "in_atmosphere" not in (recounts["D1"]["status"], recounts["D2"]["status"]):
        parts_d, facts_d, srcs_all = {}, {"investigations_in_psi": ctx.n_investigations}, []
        for nid in ("D1", "D2"):
            ids = recounts[nid]["usable"]
            srcs = sorted({ctx.test[t]["source_id"] for t in ids})
            missing = [T.VARIABLE_WORD[v] for v in ("o2_pct", "pressure_kpa")
                       if ids and all(v not in ctx.source_vars(s) for s in srcs)]
            invs = sorted({ctx.test[t]["investigation_id"] for t in ids}, key=acc_key)
            parts_d[nid] = {"n": len(ids), "invs": [ctx.name(a) for a in invs], "missing": missing}
            facts_d.update({f"{nid.lower()}_counted_tests": len(ids), f"{nid.lower()}_investigations": invs,
                            f"{nid.lower()}_not_columns": missing})
            srcs_all += [f"{F_SOURCES}#{s}" for s in srcs]
        out.append({"text": T.gap_detection(parts_d["D1"], parts_d["D2"]),
                    "needed_data": T.GAP_DETECTION_NEEDED,
                    "sources": [f"{F_REFS}#CP2003.detection", f"{F_SCEN_NEEDS}#{sc_id}/D1", f"{F_SCEN_NEEDS}#{sc_id}/D2"]
                    + srcs_all,
                    "rule": "detection", "status": "from_rule", "facts": facts_d, "text_origin": "template"})
    # not covered (needs.json _meta.not_covered), copied as written, except the lines a review found unsupported
    for nc in ctx.needs_doc["_meta"].get("not_covered", []):
        if gravity_gap and nc["source_item"] == "TB008.gaps":
            continue  # the same NASA gap is the gravity entry above
        if nc["source_item"] in REWORDED_NOT_COVERED:
            out.append(REWORDED_NOT_COVERED[nc["source_item"]](ctx, nc))
            continue
        text = T.gap_not_covered(nc["area"], nc["why"])
        # a copied line can name a test by its number ('Test 1'); the numerals are recorded as copied
        # wording, so the template number check has them and nobody reads them as a count
        copied_nums = unique(re.findall(r"(?<![\w.\-])\d+(?:\.\d+)?(?![\w])", text))
        out.append({"text": text, "needed_data": T.GAP_NOT_COVERED_NEEDED,
                    "sources": [f"{F_NEEDS}#not_covered", not_covered_source(ctx, nc["source_item"])],
                    "rule": "copied_from_needs_json_not_covered", "status": "copied",
                    "facts": ({"numerals_as_written_in_needs_json": [float(x) if "." in x else int(x)
                                                                    for x in copied_nums]} if copied_nums else {}),
                    # review (14 Nov): code-built text carries text_origin 'template' (the page tags anything
                    # else as AI-generated); copied_from says that the line is the team's spec text, as written
                    "text_origin": "template", "copied_from": f"{F_NEEDS}#not_covered"})
    return out


# Two not_covered lines of pipeline/spec/needs.json (the data role's text) are not copied as written: the review
# of 14 November (data role, reviewer notes in ai/review/review_sheet.csv) found that 'every test in the PSI tables
# is a microgravity test' and 'Required monitoring targets; the PSI tables record ...' say more than the data and
# the cited item support. The area is still taken from needs.json; the rest is built here from the files it rests
# on, and the build stops when those files no longer support the wording.
GAS_COLUMN_PREFIX = (("co_", "carbon monoxide"), ("co2_", "carbon dioxide"))


def mapped_gravity_tests(ctx):
    """The number of mapped tests, after checking that the gravity level of every table with tests is the table
    constant 'microgravity' of the source mapping (sources.json 'constants') and never a column."""
    for sid in sorted({t["source_id"] for t in ctx.tests}):
        src = ctx.source[sid]
        if src.get("constants", {}).get("gravity_level") != "microgravity":
            stop(f"{F_SOURCES} {sid}: gravity_level is not the table constant 'microgravity'; the partial-gravity gap "
                 "no longer holds")
        for c in src.get("columns", []):
            to = c["to"] if isinstance(c["to"], list) else [c["to"]]
            if "gravity_level" in to:
                stop(f"{F_SOURCES} {sid}: gravity_level is read from a column; the partial-gravity gap no longer holds")
    if any(t["gravity_level"] != "microgravity" for t in ctx.tests):
        stop("a mapped test is not set to microgravity; the partial-gravity gap no longer holds")
    return len(ctx.tests)


def recorded_product_gases(ctx):
    """The combustion-product gases that have a value in a mapped test, in words, from the non-condition gas
    readings of variables.json (oxygen readings are not products). An unknown gas reading, or a value in the
    smoke column, stops the build."""
    var = _json(F_VARIABLES)
    found = set()
    for k, v in list(var["variables"].items()) + list(var["derived"].items()):
        if v.get("kind") == "condition" or k.startswith("o2_"):
            continue
        if k == "smoke_particle_size_um":
            if any((t.get(k) or "").strip() for t in ctx.tests):
                stop("a mapped test now has a smoke particle size; the products gap no longer holds")
            continue
        if v.get("unit") not in ("ppm", "% by volume", "percentage points", "mol/mol"):
            continue
        gas = next((g for p, g in GAS_COLUMN_PREFIX if k.startswith(p)), None)
        if gas is None:
            stop(f"{F_VARIABLES} {k}: a gas reading the products gap does not name")
        if any((t.get(k) or "").strip() for t in ctx.tests):
            found.add(gas)
    return [g for _, g in GAS_COLUMN_PREFIX if g in found]


def gap_partial_gravity(ctx, nc):
    n = mapped_gravity_tests(ctx)
    return {"text": T.gap_partial_gravity(nc["area"], n), "needed_data": T.GAP_NOT_COVERED_NEEDED,
            "sources": [f"{F_NEEDS}#not_covered", f"{F_REFS}#TB008.gaps", f"{F_SOURCES}#purpose"],
            "rule": "not_covered_reworded:TB008.gaps", "status": "from_rule", "facts": {"mapped_tests": n},
            "text_origin": "template", "area_from": f"{F_NEEDS}#not_covered"}


def gap_monitoring_targets(ctx, nc):
    item = ctx.refs.get(nc["source_item"])
    doc = ctx.ref_doc.get(nc["source_item"])
    if not item or not doc:
        stop(f"references.json has no item {nc['source_item']}")
    m = re.search(r"\(([^)]+)\)\s*$", nc["area"])
    gases = [g.strip() for g in m.group(1).split(",")] if m else []
    if not gases or any(g not in item["text"] for g in gases):
        stop(f"{nc['source_item']}: the item does not give a range for every gas the area names ({gases})")
    recorded = recorded_product_gases(ctx)
    if not recorded:
        stop("no product gas has a value in the mapped tests; the products gap no longer holds")
    title = doc["title"].split(",")[0].strip()
    return {"text": T.gap_monitoring_targets(nc["area"], title, doc["id"], recorded),
            "needed_data": T.GAP_NOT_COVERED_NEEDED,
            "sources": [f"{F_NEEDS}#not_covered", f"{F_REFS}#{nc['source_item']}"],
            "rule": f"not_covered_reworded:{nc['source_item']}", "status": "from_rule",
            "facts": {"gases_with_a_range_in_the_item": gases, "product_gases_recorded": recorded,
                      "document": doc["id"]},
            "text_origin": "template", "area_from": f"{F_NEEDS}#not_covered"}


REWORDED_NOT_COVERED = {"TB008.gaps": gap_partial_gravity, "3001.T6.2-3": gap_monitoring_targets}


def in_range(v, r):
    """pipeline/run.py in_range: min inclusive and max exclusive unless the spec says otherwise."""
    lo, hi = r.get("min"), r.get("max")
    if lo is not None and (v < lo or (v == lo and not r.get("min_inclusive", True))):
        return False
    if hi is not None and (v > hi or (v == hi and not r.get("max_inclusive", False))):
        return False
    return True


def _ref_note(ctx, item_id):
    """The item's own note plus the note of the reference it belongs to (the data role's caveats)."""
    out = [str((ctx.refs.get(item_id) or {}).get("note", ""))]
    for r in _json(F_REFS)["references"]:
        if any(it["id"] == item_id for it in r.get("items", [])):
            out.append(str(r.get("note", "")))
    return " ".join(out)


def drop_test_comparison(ctx, gravity):
    """Olson and Ferkul, Table I (references.json OF2012.table1): for each material, are both limits
    (ULOI*, MOC*) at this gravity level lower than at 1 g, and lower than at both 1 g and 0 g?
    Returns the wording choices and facts, or None when the item, a key or the comparison is missing.
    No value of the table is printed."""
    it = ctx.refs.get("OF2012.table1")
    key = {"lunar": "lunar", "martian": "martian"}.get(gravity)
    if not it or not key or not resmod.check(f"{F_REFS}#OF2012.table1"):
        return None
    rows = (it.get("values") or {}).get("rows") or []
    one, both = [], []
    try:
        for r in rows:
            lu, lm = r[f"uloi_star_o2_pct_{key}"], r[f"moc_star_o2_pct_{key}"]
            b1 = lu < r["uloi_o2_pct_1g"] and lm < r["moc_o2_pct_1g"]
            b0 = lu < r["uloi_star_o2_pct_0g"] and lm < r["moc_star_o2_pct_0g"]
            one.append(b1)
            both.append(b1 and b0)
    except (KeyError, TypeError):
        return None
    if not rows or not any(one):
        return None

    def word(flags):
        return "every" if all(flags) else "some" if any(flags) else None
    text, note = it.get("text", ""), _ref_note(ctx, "OF2012.table1")
    m = re.search(r"(\d+(?:\.\d+)?) s drop tower tests", text)
    seconds = float(m.group(1)) if m else None
    wording = {"below_one_g": word(one), "below_both": word(both), "seconds": seconds,
               "criteria_caveat": "not the same as in 1g" in text,
               "ai_read": "not checked by a human" in note,
               # reader: how many materials the table has, and where the paper is (said only if the url says so)
               "n_materials": len(rows),
               "on_ntrs": "ntrs.nasa.gov" in str(_ref_parent("OF2012.table1").get("url", ""))}
    facts = {"of2012_gravity_level": key, "of2012_lower_than_one_g": word(one),
             "of2012_lower_than_one_g_and_zero_g": word(both) or "none",
             "of2012_rows_compared": "every row of values.rows of the item (one row per material)",
             "of2012_rule": "both limits of the material (ULOI*, MOC*) at this gravity level are lower",
             "of2012_materials_in_table": len(rows),
             "of2012_fig6_averages_used": False}
    if seconds is not None:
        facts["of2012_drop_seconds"] = seconds
    return {"wording": wording, "facts": facts}


def saffire_in_bins(ctx, sc):
    """Samples of the Saffire IV to VI item (references.json SAF456.conditions) whose oxygen and pressure
    fall inside this scenario's team bins, or None. Checks that none of the investigations used here is
    one of these flights; if one is, nothing is written (the sentence would be wrong)."""
    it = ctx.refs.get("SAF456.conditions")
    o2r, pr = sc["ranges"].get("o2_pct"), sc["ranges"].get("pressure_kpa")
    if not it or not o2r or not pr or not resmod.check(f"{F_REFS}#SAF456.conditions"):
        return None
    late = re.compile(r"(saffire|spacecraft fire (safety )?experiment)[\s-]*(iv|v|vi)\b", re.I)
    if any(late.search(f"{i.get('title', '')} {i.get('acronym', '')}") for i in ctx.manifest["investigations"]):
        return None
    rows = [r for r in (it.get("values") or {}).get("rows") or []
            if isinstance(r.get("o2_pct"), (int, float)) and isinstance(r.get("pressure_kpa"), (int, float))
            and in_range(r["o2_pct"], o2r) and in_range(r["pressure_kpa"], pr)
            and r.get("flight") and r.get("flight_sample")]
    if not rows:
        return None
    note = _ref_note(ctx, "SAF456.conditions")
    every = (it.get("values") or {}).get("rows") or []
    # reader: the paper's title, from references.json (the part before the author list), so the reader is
    # told what ICES-2024-365 is; None when the reference has no title
    title = str(_ref_parent("SAF456.conditions").get("title", "")).split(" (")[0].strip() or None
    return {"flights": unique(r["flight"] for r in rows),
            "samples": [(r["flight_sample"], float(r["o2_pct"]), float(r["pressure_kpa"])) for r in rows],
            "n_samples": len(every), "ai_read": "not checked by a human" in note, "paper_title": title}


def not_covered_source(ctx, item):
    """A needs.json not_covered 'source_item' as a source string: a references.json item id, or (since the
    13:06 merge) a PSI record field written as 'PSI-26 record, researchImpacts'. Anything else stops the build."""
    if item in ctx.refs:
        return f"{F_REFS}#{item}"
    m = re.fullmatch(r"(PSI-\d+) record, (\w+)", item or "")
    if m and m.group(2) in evmod.FIELDS:
        return f"{m.group(1)}.{m.group(2)}"
    stop(f"needs.json not_covered source_item {item!r} is neither a references.json item nor 'PSI-n record, field'")


# ====================================================================== result notes

def noted_entries(out):
    top = out["results"]
    top_ids = [r["psi_accession"] for r in top]
    s3 = top[-1]["score"]
    near = [r for r in out["ranking"] if r["psi_accession"] not in top_ids
            and round(abs(r["score"] - s3), 1) < NEAR_TIE_POINTS]
    return top, near


def note_for(ctx, sc_id, entry, out, in_top, g):
    acc = entry["psi_accession"]
    sc = ctx.scen[sc_id]
    conf = ctx.configs.get(entry["config_id"])
    if conf is None:
        stop(f"{entry['config_id']} is not in configurations.csv")
    parts = [T.note_phase(conf["fuel_phase"], conf["surrogate_for"])]
    sources = [f"{F_CONFIGS}#{entry['config_id']}"]
    facts, rules = {}, [f"phase:{conf['fuel_phase']}" + (f"/surrogate:{conf['surrogate_for']}" if conf["surrogate_for"] else "")]
    srcs = ctx.sources_of.get(acc, [])
    units = {s["row_unit"] for s in srcs}
    if not srcs:
        parts.append(T.NOTE_NO_TABLE)
        rules.append("row_unit:none")
        sources.append(acc)
    elif units - set(T.ROW_UNITS):
        stop(f"unknown row_unit {units} for {acc}")
    elif len(units) > 1:
        stop(f"{acc} mixes row units {units}; no template")
    elif units == {"test"}:
        rules.append("row_unit:test")
        tests = ctx.tests_of(acc)
        marks = ctx.scen_tests[sc_id]
        sources += [f"{F_SOURCES}#{s['id']}" for s in srcs] + [f"{F_SCEN_TESTS}#{sc_id}"]
        stream = [t for t in tests if t["o2_basis"] == "oxidizer_stream"]
        if not sc["ranges"]:
            parts.append(T.note_test_no_ranges(len(tests)))
            facts["tests"] = len(tests)
        else:
            amb = [t for t in tests if t["o2_basis"] == "ambient" and t["o2_pct"]]
            k = sum(marks[t["test_id"]]["tier"] == "atmosphere" for t in tests)
            k_oxy = sum(marks[t["test_id"]]["tier"] == "oxygen_only" for t in tests)
            if any(marks[t["test_id"]]["tier"] in ("atmosphere", "oxygen_only") and t["o2_basis"] != "ambient" for t in tests):
                stop(f"{acc}: a non-ambient test is counted inside the oxygen bin")
            if amb:
                ptxt, pf, ps = missing_clause(ctx, [t["test_id"] for t in amb], "pressure_kpa")
                # reader (decision 14:15): the caveat goes wherever the count of matched tests is shown
                caveat, b = None, challenge_bound(ctx, sc_id)
                in_bins = [t["test_id"] for t in tests if marks[t["test_id"]]["tier"] == "atmosphere"]
                span = bound_span(ctx, b, in_bins, sc_id) if b and in_bins else None
                if span and span["all_above"]:
                    caveat = T.bound_short(span["o2"], span["kpa"], span["atm"], span["above"], b["psi"], b["kpa"])
                    facts.update(span["facts"])
                    sources += span["sources"]
                elif span and span["all_at_or_below"]:
                    # reader 2: tests inside the bins that were recorded below the challenge-statement pressure
                    # (PSI-159 in the lunar-habitat bins): where they were recorded, and that none is counted
                    counted_none = not any(t in b["counted"] for t in in_bins)
                    caveat = T.bound_short_below(span["o2"], span["kpa"], span["atm"], b["psi"], b["kpa"], counted_none)
                    facts.update(span["facts"])
                    if counted_none:
                        facts["tests_inside_bins_counted_for_a_need"] = 0
                    sources += span["sources"]
                parts.append(T.note_test_ambient(k, len(amb), k_oxy, ptxt, caveat))
                facts.update(tests_ambient_o2=len(amb), tests_atmosphere=k, tests_oxygen_only=k_oxy, **pf)
                sources += ps
            else:
                plain = [t for t in tests if t["o2_basis"] != "oxidizer_stream"]
                if plain:
                    sids = {t["source_id"] for t in plain}
                    miss = [T.VARIABLE_WORD[v] for v in ("o2_pct", "pressure_kpa")
                            if not any(v in ctx.source_vars(s) for s in sids)]
                    if len(miss) == 2:
                        m = "oxygen and pressure are not columns in it"
                    elif miss:
                        m = f"{miss[0]} is not a column in it"
                    else:
                        m = "its oxygen cells are empty"
                    parts.append(T.note_test_no_ambient(len(plain), m))
                    facts["tests"] = len(plain)
            if stream:
                parts.append(T.note_stream(len(stream)))
                facts["tests_inverse_flame"] = len(stream)
    elif units == {"test_day"}:
        rules.append("row_unit:test_day")
        src = srcs[0]
        td = test_day_table(ctx, src)
        s = T.note_test_day(td["days"], td["flames"])
        facts["test_days"] = td["days"]
        if td["flames"] is not None:
            facts["flames_ignited"] = td["flames"]
        extra = []
        if td["o2"]:
            extra.append(T.note_test_day_oxygen(td["o2"]["min"], td["o2"]["max"], td["o2"]["as_written"],
                                                td["o2_approximate_ignited"]))
            facts.update(o2_setting_min=td["o2"]["min"], o2_setting_max=td["o2"]["max"],
                         o2_cells_as_written=td["o2"]["as_written"])
        if td["pressure_phrase"]:
            extra.append(T.note_test_day_pressure(td["pressure_phrase"]))
            facts["pressure_note_as_written"] = td["pressure_phrase"]
        parts.append(s + (": " + ", and ".join(extra) if extra else "") + ".")
        sources.append(f"{F_SOURCES}#{src['id']}")
    else:
        (u,) = units
        rules.append(f"row_unit:{u}")
        src = srcs[0]
        rows = table_rows(src)
        parts.append(T.NOTE_ROW_UNIT[u].format(rows=rows))
        facts["table_rows"] = rows
        sources.append(f"{F_SOURCES}#{src['id']}")
    # sentence 3: stated objectives
    links = ctx.links_of(acc)
    nids = unique(r["need_id"] for r in links)
    in_rec = [n for n in nids if any((r.get("record_field") or "").strip() for r in links if r["need_id"] == n)]
    pub_only = [n for n in nids if n not in in_rec]
    word = lambda n: f"{n} ({ctx.need[n]['name'] if n in ctx.need else n})"  # noqa: E731
    parts.append(T.note_objectives([word(n) for n in in_rec], [word(n) for n in pub_only]))
    for r in links:
        sources += ctx.link_sources(r)
    facts["needs_stated"] = nids
    if pub_only:
        facts["needs_stated_in_a_publication_only"] = pub_only
    # sentence 4: ties, without numbers
    ties = [r["investigation_id"] for r in out["ranking"]
            if r["psi_accession"] != acc and round(r["score"], 1) == round(entry["score"], 1)]
    if ties:
        parts.append(T.note_tie(ties))
        rules.append("tie")
    if not in_top:
        parts.append(T.NOTE_NEAR)
        rules.append("near_tie")
    # sentence 5: the scorer's atmosphere fallback, only where that dimension is weighted
    weighted = {k.lower() for k in entry.get("weights_used", {})}
    dims = [d for d in entry.get("assumed_dims", []) if d.lower() in weighted]
    if dims:
        parts.append(T.note_assumed(dims))
        sources.append(f"{F_SCORING}#atmosphere_fallback")
        rules.append("assumed_dims")
    # fixed weak-scenario sentences (review: on every note of the scenario, near-ties included, so a
    # note shown under 'Other investigations' carries the same caveat)
    if sc_id == "spacesuit":
        o2r = sc["ranges"]["o2_pct"]
        if g["max_ambient_o2"][0] >= o2r["min"] or g["max_stream_o2"][0] >= o2r["min"]:
            stop("a test now has oxygen in the spacesuit bin: the fixed spacesuit sentence no longer holds")
        parts.append(T.note_spacesuit(o2r["min"], o2r["max"]))
        facts["team_bins"] = bins_facts({"o2_pct": o2r})
        rules.append("fixed:spacesuit")
    if sc_id == "mars_habitat":
        if (any(set(r["weights_used"]) != {"flow", "role"} for r in out["results"])
                or "o2_pct" in out["scenario"] or "pressure_kpa" in out["scenario"]):
            stop("the Mars ranking now uses an atmosphere: the fixed Mars sentence no longer holds")
        parts.append(T.NOTE_MARS)
        rules.append("fixed:mars_habitat")
    return {"investigation_id": acc, "text": " ".join(parts), "sources": unique(sources), "facts": facts,
            "text_origin": "template", "status": "top3" if in_top else "near_tie", "rule": rules,
            "config_id": entry["config_id"]}


def result_notes(ctx, sc_id, out, g):
    top, near = noted_entries(out)
    notes = [note_for(ctx, sc_id, r, out, True, g) for r in top]
    notes += [note_for(ctx, sc_id, r, out, False, g) for r in near]
    return notes


# ====================================================================== scenarios

def scenario_inputs():
    """The files whose content the scenario text depends on (hashed into fresh.scenario_inputs_sha256)."""
    return list(SCENARIO_INPUTS) + [f"{F_PACKAGES}/index.json"] + package_files()


def fresh(ctx):
    cat = {p: metamod.sha256_file(ROOT / p) for p in (F_CONFIGS, F_INVEST)}
    scen = {p: metamod.sha256_file(ROOT / p) for p in scenario_inputs()}
    return {"ranker_config_version": ctx.scoring.get("version"),
            "scoring_config_sha256": metamod.sha256_file(ROOT / F_SCORING),
            "catalog_sha256": metamod.sha256_json(cat),
            "scenario_inputs_sha256": metamod.sha256_json(scen),
            "hash_rule": ("catalog_sha256 and scenario_inputs_sha256 are ai.meta.sha256_json of {repo path: file sha256} "
                          f"over {list(cat)} and {list(scen)}")}


def scenario_entry(ctx, sc_id, query, g, fr):
    from scoring import scorer  # imported, never changed
    out = scorer.rank(query)
    if out.get("status") != "ok" or out["scenario"].get("preset") != sc_id:
        stop(f"rank({query!r}) did not return preset {sc_id}")
    recounts = {n["id"]: recount(ctx, sc_id, n["id"]) for n in ctx.needs}
    needs_out = [need_entry(ctx, sc_id, n) for n in ctx.needs]
    ftext, fsrc, ffacts = frame(ctx, sc_id, g)
    return {
        "id": sc_id, "query": query, "ranking_source": "scoring.scorer.rank",
        "frame": ftext, "frame_sources": fsrc, "frame_facts": ffacts,
        "result_notes": result_notes(ctx, sc_id, out, g),
        "needs": needs_out,
        "gaps": gaps(ctx, sc_id, needs_out, recounts, g),
        # review (14 Nov): every sentence of an entry is built by team code (no language model), so the entry
        # says text_origin 'template' and ai_generated false; that the code itself was written with an AI
        # assistant is in the disclosure block (data/insights/_meta.json) and in the label
        "ai_generated": False, "text_origin": "template", "frame_text_origin": "template",
        "model": T.SCENARIO_MODEL, "built_by": T.BUILT_BY, "reviewed_by": None,
        "label": T.SCENARIO_LABEL, "updated": None, "fresh": fr,
    }


# ====================================================================== cards

def _span(raw, start, end):
    return ws(raw[start:end])


def quote_span(ctx, acc, field, us, i):
    """Verbatim span for unit us[i]: with its list lead-in when that line is right before it.
    Returns (text, char_start, char_end, [units])."""
    u = us[i]
    raw = ctx.record(acc)[field]
    if raw[u["char_start"]:u["char_end"]] != u["text"]:
        stop(f"{acc} {u['id']}: offsets do not reproduce the unit text")
    start, used = u["char_start"], [u]
    if u.get("under_heading"):
        h = next((x for x in us if x["id"] == u["under_heading"]), None)
        if h and raw[h["char_end"]:u["char_start"]].strip() in ("", u.get("list_marker") or ""):
            start, used = h["char_start"], [h, u]
    return _span(raw, start, u["char_end"]), start, u["char_end"], used


def extend_span(ctx, acc, field, us, i, start, used):
    """Join the next quotable unit after us[i] when it follows directly (only a list marker between)."""
    raw = ctx.record(acc)[field]
    u = us[i]
    m = u.get("list_marker")
    if start == u["char_start"] and m:  # joined list items: start at the first item's own marker
        k = raw.rfind(m, 0, u["char_start"])
        if k >= 0 and not raw[k + len(m):u["char_start"]].strip():
            start = k
    for j in range(i + 1, len(us)):
        v = us[j]
        if not v["quotable"]:
            return None
        if raw[u["char_end"]:v["char_start"]].strip() in ("", v.get("list_marker") or ""):
            return _span(raw, start, v["char_end"]), start, v["char_end"], used + [v]
        return None
    return None


def sentence(acc, role, field, label, text, cs, ce, used):
    shared = sorted({s for u in used for s in u.get("shared_with", [])}, key=acc_key)
    return {"role": role, "origin": "quote", "text": text, "field_label": label,
            "source": f"{acc}.{field}", "char_start": cs, "char_end": ce,
            "evidence": [{"id": u["id"], "source": u["source"], "quote": u["text"],
                          "char_start": u["char_start"], "char_end": u["char_end"]} for u in used],
            "checks": {"verbatim_span": True, "whitespace": "runs of spaces and line breaks shown as one space"},
            "lexical_support": 1.0, "shared_with": shared, "review": None}


# review: the label 'Stated objective:' / 'Stated hypothesis:' names the record field, but the first
# sentence of a field is not always an objective or a hypothesis (PSI-25's objective field opens with
# 'BASS-II results contribute to ...'; PSI-47's hypothesis field opens with how the instrument works).
# The pick is still a fixed rule over verbatim sentences: the first quotable unit that says it is an
# objective or a hypothesis (or is a list item under such a heading), else the first quotable unit.
OBJECTIVE_CUE = re.compile(r"\b(objectives?|goals?|aims?|aimed|seeks?|sought|purpose|focus)\b", re.I)
HYPOTHESIS_CUE = re.compile(r"hypothesi[sz]e[sd]?\b|hypothes[ie]s\b(?!\s+used)", re.I)
FIELD_CUES = {"objective": OBJECTIVE_CUE, "hypothesis": HYPOTHESIS_CUE}


def pick_unit(us, field):
    """Index of the unit to quote for this field, and the rule that picked it."""
    qi = [i for i, u in enumerate(us) if u["quotable"]]
    if not qi:
        return None, None
    cue = FIELD_CUES.get(field)
    if cue:
        by_id = {u["id"]: u for u in us}
        for i in qi:
            u = us[i]
            head = by_id.get(u.get("under_heading") or "")
            if cue.search(u["text"]) or (head is not None and cue.search(head["text"])):
                return i, ("first quotable unit" if i == qi[0] else f"first quotable unit that names the {field}")
    return qi[0], "first quotable unit"


def card(ctx, acc):
    rec = ctx.ev["records"][acc]
    sentences = []
    picks = {}
    obj = evmod.units(acc, "objective", ev=ctx.ev)
    qi = [i for i, u in enumerate(obj) if u["quotable"]]
    if not qi:
        stop(f"{acc} has no quotable objective sentence")
    i, picks["objective"] = pick_unit(obj, "objective")
    qi = [j for j in qi if j >= i]
    text, cs, ce, used = quote_span(ctx, acc, "objective", obj, i)
    quotes = []
    if obj[i]["words"] < SHORT_QUOTE_WORDS and len(qi) > 1:
        joined = extend_span(ctx, acc, "objective", obj, i, cs, used)
        if joined:
            text, cs, ce, used = joined
            quotes = [text]
        else:
            t2, cs2, ce2, used2 = quote_span(ctx, acc, "objective", obj, qi[1])
            sentences.append(sentence(acc, "summary", "objective", evmod.FIELDS["objective"][1], text, cs, ce, used))
            text, cs, ce, used = t2, cs2, ce2, used2
            quotes = [sentences[0]["text"], text]
    if not quotes:
        quotes = [text]
    sentences.append(sentence(acc, "summary", "objective", evmod.FIELDS["objective"][1], text, cs, ce, used))
    key_points = []
    for field in ("approach", "hypothesis", "researchImpacts"):
        us = evmod.units(acc, field, ev=ctx.ev)
        j, picks[field] = pick_unit(us, field)
        if j is None:
            del picks[field]
            continue
        label = evmod.FIELDS[field][1]
        t, a, b, used = quote_span(ctx, acc, field, us, j)
        sentences.append(sentence(acc, "key_point", field, label, t, a, b, used))
        key_points.append({"text": T.key_point(label, t), "source": f"{acc}.{field}"})
    return {
        "investigation_id": acc,
        "summary": T.card_summary(quotes),
        "key_points": key_points,
        "ai_generated": False,
        "model": T.CARD_MODEL,
        "reviewed_by": None,
        "updated": None,
        "summary_sources": [f"{acc}.objective"],
        "built_by": T.BUILT_BY,
        "status": "fallback_quote",
        "sentences": sentences,
        "label": T.CARD_LABEL,
        "prompt_sha256": None,
        "params": {},
        "license_note": T.license_note(rec["license"]),
        "pick_rule": picks,
        "record_title": rec["title"],
        "dataset_doi": rec.get("dataset_doi"),
    }


# ====================================================================== checks, write

def all_sources(obj):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("sources", "frame_sources", "summary_sources") and isinstance(v, list):
                out += v
            elif k == "source" and isinstance(v, str):
                out.append(v)
            else:
                out += all_sources(v)
    elif isinstance(obj, list):
        for v in obj:
            out += all_sources(v)
    return out


def check_sources(payload):
    bad = []
    for s in unique(all_sources(payload)):
        try:
            resmod.resolve(s)
        except (resmod.SourceNotFound, resmod.BadSource) as e:
            bad.append(f"{s}: {e}")
    if bad:
        stop("sources that do not resolve:\n  " + "\n  ".join(bad))


def keep_updated(new, path, key):
    """Keep each entry's earlier 'updated' time when nothing else in it changed (byte-identical reruns)."""
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    old = {}
    if path.exists():
        try:
            old = {e[key]: e for e in json.loads(path.read_text(encoding="utf-8"))}
        except (ValueError, KeyError, TypeError):
            old = {}
    for e in new:
        o = old.get(e[key])
        same = o and {k: v for k, v in o.items() if k != "updated"} == {k: v for k, v in e.items() if k != "updated"}
        e["updated"] = o["updated"] if same else now
    return new


def build(ctx=None, scenario_ids=None):
    ctx = ctx or Ctx()
    g = global_facts(ctx)
    fr = fresh(ctx)
    scenarios, skipped = [], []
    for sc_id, query in T.QUERIES:
        if scenario_ids and sc_id not in scenario_ids:
            continue
        if sc_id not in ctx.scen or not any(k[0] == sc_id for k in ctx.scen_needs):
            skipped.append(sc_id)
            continue
        scenarios.append(scenario_entry(ctx, sc_id, query, g, fr))
    cards = [card(ctx, acc) for acc in sorted(ctx.ev["records"], key=acc_key)]
    check_sources(scenarios)
    check_sources(cards)
    return {"scenarios": scenarios, "cards": cards, "skipped": skipped, "global": g, "ctx": ctx,
            "warnings": list(ctx.warnings)}


def write(res):
    scen = keep_updated(res["scenarios"], OUT_SCENARIOS, "id")
    cards = keep_updated(res["cards"], OUT_CARDS, "investigation_id")
    inputs_s = scenario_inputs() + [F_OBJ_LINKS, F_SOURCES, F_REFS, F_VARIABLES, F_SCORING, F_CONFIGS, F_INVEST, F_MANIFEST,
                                        F_EVIDENCE, f"{TABLE_DIR}/PSI-20_Experimental table_ACME BRE.csv",
                                        "scoring/scorer.py"]
    bs = metamod.meta(T.BUILT_BY, config.NO_MODEL, inputs_s, label=(
        "AI-generated data file: built by code written with an AI assistant (Claude Code); no language model ran. "
        "Counts are computed by code from the pipeline CSVs and NASA PSI tables and every sentence is a fixed "
        "template filled with those counts or copied NASA text. " + T.SCENARIO_LABEL),
        entries=[e["id"] for e in scen], text_origin="template")
    metamod.write_json(OUT_SCENARIOS, scen, bs)
    inputs_c = [F_EVIDENCE, F_MANIFEST] + [f"data/psi/catalog/{c['investigation_id']}.json" for c in cards]
    bc = metamod.meta(T.BUILT_BY, config.NO_MODEL, inputs_c, label=(
        "AI-generated data file: built by code written with an AI assistant (Claude Code); no language model ran. "
        "Every card is verbatim text quoted from its NASA PSI record, chosen by fixed rules, with the record field "
        "of each quote. Team output, not a NASA conclusion."),
        entries=len(cards), status="fallback_quote")
    metamod.write_json(OUT_CARDS, cards, bc)
    return scen, cards


# ====================================================================== report

def report(res, ids_full):
    # The design's expected values (computed from d98a216, before the data role's audit) are no longer
    # printed: the build recounts every row and stops when scenario_needs.csv or the evidence package
    # differs from its own count, so the counts below are the current ones.
    print("== counts per need (recounted from tests.csv, need_tests.csv and scenario_tests.csv; equal to "
          "scenario_needs.csv and the evidence packages)")
    for e in res["scenarios"]:
        if e["id"] not in ids_full:
            continue
        for n in e["needs"]:
            row = res["ctx"].scen_needs[(e["id"], n["need_id"])]
            print(f"  {e['id']:14s} {n['need_id']:3s} {row['status']:17s} counted {row['usable_tests']:>4s}  "
                  f"atmosphere {row['tests_atmosphere']:>3s}  oxygen_only {row['tests_oxygen_only']:>3s}  "
                  f"pressure_only {row['tests_pressure_only']:>3s}  other {row['tests_other']:>4s}  "
                  f"outside objective {row['tests_recorded_outside_objective']:>4s}  gaps {row['gaps'] or '-'}")
    g = res["global"]
    print(f"  solid tests {g['solid_tests']}, with pressure {g['solid_tests_with_pressure']}; highest solid oxygen "
          f"{g['max_solid_o2']}; highest ambient oxygen {g['max_ambient_o2']}; highest burner-stream oxygen {g['max_stream_o2']}")
    for e in res["scenarios"]:
        full = e["id"] in ids_full
        print(f"\n==================== {e['id']} (query {e['query']!r})")
        if not full:
            print(f"  {len(e['needs'])} needs, {len(e['gaps'])} gaps, {len(e['result_notes'])} notes (use --print-all)")
            continue
        print("FRAME:", e["frame"])
        print("  sources:", e["frame_sources"])
        print("NEEDS:")
        for n in e["needs"]:
            print(f"  [{n['need_id']}] ({n['status']}) {n['statement']}")
            print(f"      facts: {json.dumps(n['facts'], ensure_ascii=False)}")
        print("GAPS:")
        for x in e["gaps"]:
            print(f"  - {x['text']}\n      needed_data: {x['needed_data']}  [rule {x['rule']}]")
        print("RESULT NOTES:")
        for x in e["result_notes"]:
            print(f"  [{x['investigation_id']} {x['status']}] {x['text']}")
    if res["skipped"]:
        print("\nskipped (no rows in the data role's files):", res["skipped"])
    print(f"\ncards: {len(res['cards'])}, status {Counter(c['status'] for c in res['cards'])}")
    for w in res.get("warnings") or []:
        print(f"WARNING (input text not owned by pm): {w}", file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="build and compare with the files on disk; write nothing")
    ap.add_argument("--print-all", action="store_true", help="print the text of every scenario")
    ap.add_argument("--print-cards", action="store_true", help="print every card")
    a = ap.parse_args(argv)
    try:
        res = build()
    except BuildStop as e:
        print(f"BUILD STOPPED: {e}", file=sys.stderr)
        return 2
    report(res, {"iss", "lunar_habitat"} | ({"spacesuit", "mars_habitat"} if a.print_all else set()))
    if a.print_cards:
        for c in res["cards"]:
            print(f"\n[{c['investigation_id']}] {c['summary']}")
            for k in c["key_points"]:
                print(f"   - {k['text']}  ({k['source']})")
    if a.check:
        ok = True
        for path, new, key in ((OUT_SCENARIOS, res["scenarios"], "id"), (OUT_CARDS, res["cards"], "investigation_id")):
            old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            strip = lambda xs: [{k: v for k, v in x.items() if k != "updated"} for x in xs]  # noqa: E731
            same = old is not None and strip(old) == strip(new)
            ok &= same
            print(f"{path.relative_to(ROOT)}: {'matches the build' if same else 'DIFFERS from the build'}")
        return 0 if ok else 1
    write(res)
    print(f"\nwrote {OUT_SCENARIOS.relative_to(ROOT)} and {OUT_CARDS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
