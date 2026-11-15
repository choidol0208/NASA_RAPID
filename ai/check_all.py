# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""One check over everything pm ships from data/insights/ (design, component B).

Standard library only. Exit 0 only if every hard check passes; exit 1 otherwise.
A file that does not exist yet is reported as 'not built yet' and does not fail.

To rebuild every file it checks, in the right order and with no model call, run
    python3 ai/build_all.py
(evidence, baseline scenarios and quoted cards, evidence map, cards from the logged model output,
catalog audit, review, then this check). A stale or failing file is fixed by that command, not by hand.

Hard checks (files pm owns):
  headers      every ai/**/*.py starts with the AI-generated-code comment line
  disclosure   every file in data/insights/ has its _meta block (inside the file when it is a JSON
               object, and in _meta.json for every file), with every field, a content_sha256 that
               matches the content, and inputs_sha256 equal to the current input files (else: stale)
  compliance   `git diff HEAD` removes no line from compliance/AI_USAGE_LOG.md, compliance/SOURCES.md
               or .gitignore (append-only files; read-only git command)
  evidence     evidence.json is what ai/evidence.py builds now; record[field][char_start:char_end]
               equals every unit text; every unit source resolves
  codes        every status and gap code in scenario_needs.csv is one the templates know
  recount      a second code path (tests.csv, need_tests.csv stated rows, pipeline/spec/scenarios.json;
               it does not read scenario_needs.csv or scenario_tests.csv) recounts usable tests and the
               four tiers and compares them with scenario_needs.csv; the anchors the wording rests on are
               compared with a third path (the data role's evidence packages and investigation_facts.json),
               and the rules the text states (no solid test with a pressure, no lunar S1 extinction, only
               ambient oxygen inside the bins) are asserted
  cards        cards.json: 24 entries in the contract shape; every quote is a verbatim unit with its
               field label; every stored evidence quote is the exact text of its unit; every model sentence
               passes gates 1-11 (recomputed from its model_quote), ends with its bracketed source, has its
               first cited unit among the key points, and has no 'not'/'partly' verdict or modality 'no';
               no sentence listed in ai/review/pm_prereview.json remains, and its slot is the quoted unit;
               no quote listed under hidden_by_review (marked not_relevant in the review sheet) is shown;
               ai_generated is true exactly when a model sentence is shown; with --final no unreviewed
               model sentence; no fact-check-model score
  sheet        ai/review/review_sheet.csv lists exactly what the cards and scenarios show (rows with shown =
               yes, matched by item and sentence_sha) plus the rows whose verdict removes their sentence
               (shown = no); no row marked not, partly, modality no or not_relevant is shown, except a card's
               last quoted summary sentence (a card never shows an empty summary; listed in quality.json)
  scenarios    scenarios.json: one entry per contract query; one need entry per need id in needs.json;
               every template statement passes check_template; every facts value is found by the
               recount (or as a numeral in a cited source); every source resolves; result-note ids equal
               the live rank() top 3 plus near-ties (within 3 points of rank 3); 'PSI holds no
               experimental table' only where sources.json has no entry; the stored fresh{} hashes
               equal the current files; every entry and item is labelled text_origin 'template' (and
               frame_text_origin, ai_generated false); every cited pipeline sentence
               (data/pipeline/evidence/...#need/statement) is in the text as written

  readiness    model_readiness.json equals a fresh build of ai/model_readiness.py (same seed) and passes its
               wording and source checks (ai/model_readiness.py check)
  robustness   robustness.json: live top 3, config version and assumed_dims equal rank() now; the shares
               rebuild by the NumPy path (ai/robustness.py check_file)
  assistant    every ai/assistant/ code file (.py, .js, .css, .sh) and install.sh, run.sh carry the
               AI-generated-code sentence; eval/questions.json has the required coverage and equals its frozen
               sha256; assistant_eval.json (when built) is a model run on that set with every question in each
               arm it has; assistant_recorded.json (when built): every response is a RESPONSE marked recorded,
               every model sentence passes the code gates against its recorded facts, and the tools re-run
               with each recorded request give the same text for every cited fact

Reported as info (never fails): a need statement whose pipeline reading says no test is counted while its
count is above zero (the data role's text; the fix is in pipeline/spec/needs.json).

Report-only (files pm does not own; never fails): the linter and the advice lexicon over the warning
strings in scoring/scoring_config.json, the why and main_gap strings of rank() for the four queries,
and the objectives and key_findings columns of data/catalog/*.csv. The hits are printed and, with
--json, returned as lint_hits [{file, key, text, pattern}] for data/insights/catalog_trace.json
(component F writes that file; check_all writes nothing).

    python3 ai/check_all.py            # human-readable report, exit code 0/1
    python3 ai/check_all.py --final    # also fail on any unreviewed model sentence (pre-freeze sync)
    python3 ai/check_all.py --json     # the full report as JSON on stdout
"""
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai import checks as C, config, evidence as evmod, llm, meta as metamod, resolve  # noqa: E402
from ai import templates as T  # noqa: E402
from ai.lint_patterns import NUMBER_WORDS as LP_NUMBER_WORDS  # noqa: E402

ROOT = config.ROOT
INSIGHTS = config.INSIGHTS_DIR
PIPE = ROOT / "data" / "pipeline"
SPEC = ROOT / "pipeline" / "spec"
META_FIELDS = ("built_by", "code_written_with", "language_model_used_at_build", "generated_at",
               "inputs_sha256", "label")
ARRAY_FILES = ("cards.json", "scenarios.json")
QUERIES = (("iss", "ISS"), ("lunar_habitat", "lunar habitat"), ("spacesuit", "spacesuit"),
           ("mars_habitat", "Mars base"))
STATUSES = T.STATUSES      # the six statuses of pipeline/spec/scenarios.json
GAP_CODES = T.GAP_CODES    # the nine gap codes of pipeline/spec/statements.json (flow codes included)
REBUILD = "python3 ai/build_all.py"
TIERS = ("atmosphere", "oxygen_only", "pressure_only", "other")
NEAR_TIE_POINTS = 3.0
NO_TABLE_PHRASE = "PSI holds no experimental table"
FORBIDDEN_SCORE_KEYS = re.compile(r"minicheck|second_opinion|nli_score|factcheck|fact_check", re.I)
VERDICT_REMOVE = ("not", "partly")
# Published conversion constants a template may carry in its facts (the only derived values check_all accepts).
CONSTANTS_PSI_KPA = 6.894757  # kPa per psi
CONSTANTS = {round(CONSTANTS_PSI_KPA, 6)}


# ====================================================================== report

class Report:
    """Collects results. level: ok | fail | not_built | info | report (report-only lint hit)."""

    def __init__(self):
        self.items = []
        self.lint_hits = []

    def add(self, level, section, message, **extra):
        self.items.append({"level": level, "section": section, "message": message, **extra})

    def ok(self, section, message, **kw):
        self.add("ok", section, message, **kw)

    def fail(self, section, message, **kw):
        self.add("fail", section, message, **kw)

    def info(self, section, message, **kw):
        self.add("info", section, message, **kw)

    def not_built(self, section, message):
        self.add("not_built", section, message)

    def failures(self):
        return [x for x in self.items if x["level"] == "fail"]


def _rel(p):
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _acc_key(acc):
    try:
        return int(str(acc).split("-")[1])
    except (IndexError, ValueError):
        return 10 ** 6


# ====================================================================== headers

def check_headers(rep, ai_dir=config.AI_DIR):
    bad, n = [], 0
    for p in sorted(Path(ai_dir).rglob("*.py")):
        if any(part.startswith(".") or part == "__pycache__" for part in p.relative_to(ai_dir).parts):
            continue
        n += 1
        first = p.read_text(encoding="utf-8").split("\n", 1)[0]
        if first != config.HEADER_COMMENT:
            bad.append(p.relative_to(ai_dir).as_posix())
    for b in bad:
        rep.fail("headers", f"{b}: first line is not the AI-generated-code comment")
    if not bad:
        rep.ok("headers", f"{n} code files in ai/ start with the AI-generated-code comment")


# ====================================================================== disclosure

def _check_block(rep, name, block, body):
    missing = [k for k in META_FIELDS if k not in (block or {})]
    if missing:
        rep.fail("disclosure", f"{name}: _meta block lacks {', '.join(missing)}")
        return
    if block["language_model_used_at_build"] not in (config.NO_MODEL, config.MODEL_LABEL):
        rep.fail("disclosure", f"{name}: language_model_used_at_build is {block['language_model_used_at_build']!r}")
    if block.get("code_written_with") != config.CODE_WRITTEN_WITH:
        rep.fail("disclosure", f"{name}: code_written_with is {block.get('code_written_with')!r}")
    if not str(block["built_by"]).startswith("ai/"):
        rep.fail("disclosure", f"{name}: built_by is {block['built_by']!r}")
    if body is not None and "content_sha256" in block and block["content_sha256"] != metamod.sha256_json(body):
        rep.fail("disclosure", f"{name}: content_sha256 does not match the content (edited after it was written)")
    stale = []
    for rel, sha in (block.get("inputs_sha256") or {}).items():
        p = ROOT / rel
        if not p.exists():
            stale.append(f"{rel} (missing)")
        elif metamod.sha256_file(p) != sha:
            stale.append(rel)
    if stale:
        rep.fail("disclosure", f"{name}: stale, inputs changed since the build: {', '.join(stale[:6])}"
                               + (f" and {len(stale) - 6} more" if len(stale) > 6 else ""))


def check_disclosure(rep, insights=INSIGHTS):
    insights = Path(insights)
    comp_path = insights / metamod.COMPANION
    if not comp_path.exists():
        rep.fail("disclosure", "data/insights/_meta.json does not exist")
        return
    companion = json.loads(comp_path.read_text(encoding="utf-8"))
    if "_meta" not in companion:
        rep.fail("disclosure", "_meta.json has no '_meta' entry for itself")
    files = sorted(p for p in insights.iterdir() if p.is_file() and not p.name.startswith(".")
                   and p.name != metamod.COMPANION)
    before = len(rep.failures())
    for p in files:
        block = companion.get(p.name)
        if block is None:
            rep.fail("disclosure", f"{p.name}: no entry in _meta.json")
            continue
        body = None
        if p.suffix == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                inner = data.get("_meta")
                if inner is None:
                    rep.fail("disclosure", f"{p.name}: JSON object without a '_meta' block")
                elif inner != block:
                    rep.fail("disclosure", f"{p.name}: its '_meta' block differs from its _meta.json entry")
                body = {k: v for k, v in data.items() if k != "_meta"}
            else:
                body = data
        _check_block(rep, p.name, block, body)
    for name in companion:
        if name != "_meta" and not (insights / name).exists():
            rep.fail("disclosure", f"_meta.json has an entry for {name}, which does not exist")
    if len(rep.failures()) == before:
        rep.ok("disclosure", f"{len(files)} files in data/insights/ carry a complete, current disclosure block: "
                             + ", ".join(p.name for p in files))


# ====================================================================== compliance (append-only files)

def check_compliance_diff(rep):
    paths = ["compliance/AI_USAGE_LOG.md", "compliance/SOURCES.md", ".gitignore"]
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "diff", "HEAD", "--", *paths],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        rep.info("compliance", f"git diff could not run ({exc}); append-only check skipped")
        return
    if out.returncode != 0:
        rep.info("compliance", f"git diff failed: {out.stderr.strip()[:200]}; append-only check skipped")
        return
    removed = [ln for ln in out.stdout.splitlines() if ln.startswith("-") and not ln.startswith("---")]
    added = [ln for ln in out.stdout.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
    if removed:
        rep.fail("compliance", f"{len(removed)} line(s) removed or changed in append-only files: {removed[0][:160]!r}")
    else:
        rep.ok("compliance", f"append-only files: {len(added)} line(s) added since HEAD, none removed")


# ====================================================================== evidence

def check_evidence(rep, ev, path=evmod.EVIDENCE_PATH):
    if ev is None:
        rep.not_built("evidence", f"{_rel(path)}: not built yet")
        return
    recs = ev["records"]
    psi = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in config.PSI_CATALOG_DIR.glob("PSI-*.json")}
    before = len(rep.failures())
    if sorted(recs, key=_acc_key) != sorted(psi, key=_acc_key):
        rep.fail("evidence", "records in evidence.json differ from data/psi/catalog/")
    n = 0
    for inv, r in recs.items():
        ids = [u["id"] for u in r["units"]]
        if len(ids) != len(set(ids)):
            rep.fail("evidence", f"{inv}: duplicate unit ids")
        for u in r["units"]:
            n += 1
            src = (psi.get(inv) or {}).get(u["field"]) or ""
            if src[u["char_start"]:u["char_end"]] != u["text"]:
                rep.fail("evidence", f"{inv} {u['id']}: field[char_start:char_end] != unit text")
            if u["source"] != f"{inv}.{u['field']}" or not resolve.check(u["source"]):
                rep.fail("evidence", f"{inv} {u['id']}: source {u['source']} does not resolve")
    try:
        rebuilt = evmod.build()["records"]
        if rebuilt != recs:
            rep.fail("evidence", "evidence.json is not what ai/evidence.py builds now (rebuild it)")
    except Exception as exc:  # report, do not hide
        rep.fail("evidence", f"ai/evidence.py build() raised {type(exc).__name__}: {exc}")
    if len(rep.failures()) == before:
        rep.ok("evidence", f"{len(recs)} records, {n} units: offsets round-trip, sources resolve, "
                           "file equals a fresh build")


# ====================================================================== independent recount

def _in_range(v, r):
    lo = r.get("min") is None or v > r["min"] or (v == r["min"] and r.get("min_inclusive", True))
    hi = r.get("max") is None or v < r["max"] or (v == r["max"] and r.get("max_inclusive", False))
    return lo and hi


def _mark(t, sc):
    """Second code path for one test against one scenario (pipeline/spec/scenarios.json _meta rules)."""
    rng = sc.get("ranges") or {}

    def m(var):
        r = rng.get(var)
        if r is None:
            return "not_specified"
        v = _num(t.get(var))
        if v is None:
            return "not_recorded"
        return "in" if _in_range(v, r) else "out"
    o, p = m("o2_pct"), m("pressure_kpa")
    if o in ("in", "out") and t.get("o2_basis") != "ambient":
        o = "not_ambient"
    if o == "in" and p == "in":
        tier = "atmosphere"
    elif o == "in" and p == "not_recorded":
        tier = "oxygen_only"
    elif p == "in" and o == "not_recorded":
        tier = "pressure_only"
    else:
        tier = "other"
    return {"o2": o, "pressure": p, "flow": m("flow_cms"), "tier": tier,
            "gravity": ("not_specified" if not sc.get("gravity_level")
                        else "same" if t.get("gravity_level") == sc["gravity_level"] else "different")}


def _diluent(t):
    co2, he = _num(t.get("co2_pct")), _num(t.get("he_pct"))
    if co2 is None and he is None:
        return "not_recorded"
    if (co2 or 0) > 0 and (he or 0) > 0:
        return "co2_and_he_added"
    if (co2 or 0) > 0:
        return "co2_added"
    if (he or 0) > 0:
        return "he_added"
    return "n2_only"


def _add_numbers(bag, values):
    for v in values:
        if isinstance(v, bool) or v is None:
            continue
        if isinstance(v, (int, float)):
            bag.add(round(float(v), 6))


def _psi_table_numbers(file_name):
    bag = set()
    p = ROOT / "data" / "psi" / "experimental_tables" / file_name
    if not p.exists():
        return bag
    with open(p, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.reader(f))
    for row in rows[1:]:
        for cell in row:
            for n in C.extract_numbers(cell):
                bag.add(round(float(n["value"]), 6))
    bag.add(float(len(rows) - 1))  # rows (test days, sessions)
    for j, h in enumerate(rows[0] if rows else []):  # column sums of integer count columns
        vals = [_num(r[j]) for r in rows[1:] if j < len(r)]
        if vals and all(v is not None and float(v).is_integer() for v in vals):
            bag.add(float(sum(vals)))
    return bag


def recount():
    """Recount from tests.csv, need_tests.csv (stated rows) and pipeline/spec/scenarios.json only."""
    tests = _read_csv(PIPE / "tests.csv")
    by_id = {t["test_id"]: t for t in tests}
    links = _read_csv(PIPE / "need_tests.csv")
    usable, outside = defaultdict(set), defaultdict(set)
    for r in links:
        (usable if r.get("objective_link") == "stated" else outside)[r["need_id"]].add(r["test_id"])
    spec = json.loads((SPEC / "scenarios.json").read_text(encoding="utf-8"))
    needs = [n["id"] for n in json.loads((SPEC / "needs.json").read_text(encoding="utf-8"))["needs"]]
    sources = json.loads((SPEC / "sources.json").read_text(encoding="utf-8"))["sources"]

    rows, marks = {}, {}
    bag_need, bag_inv, bag_scen = defaultdict(set), defaultdict(set), defaultdict(set)
    for sc in spec["scenarios"]:
        sid = sc["id"]
        mk = {t["test_id"]: _mark(t, sc) for t in tests}
        marks[sid] = mk
        for rng in (sc.get("ranges") or {}).values():
            _add_numbers(bag_scen[sid], [rng.get("min"), rng.get("max")])
        _add_numbers(bag_scen[sid], (sc.get("nominal") or {}).values())
        for need in needs:
            ids = usable.get(need, set())
            row = {"usable_tests": len(ids), "tests_recorded_outside_objective": len(outside.get(need, set()))}
            bag = bag_need[(sid, need)]
            for tier in TIERS:
                hit = [i for i in ids if mk[i]["tier"] == tier]
                row[f"tests_{tier}"] = len(hit)
                row[f"investigations_{tier}"] = ";".join(sorted({by_id[i]["investigation_id"] for i in hit},
                                                                key=_acc_key))
                _add_numbers(bag, [len(hit)])
                for key in ("investigation_id", "fuel_phase", "test_end", "flow_event", "o2_basis", "source_id"):
                    _add_numbers(bag, Counter(by_id[i].get(key) for i in hit).values())
                _add_numbers(bag, Counter(_diluent(by_id[i]) for i in hit).values())
                _add_numbers(bag, [sum(_diluent(by_id[i]) not in ("n2_only", "not_recorded") for i in hit)])
            best = [i for i in ids if mk[i]["tier"] in ("atmosphere", "oxygen_only")]
            for group in (ids, best, [i for i in ids if mk[i]["tier"] == "other"]):
                for key in ("investigation_id", "fuel_phase", "test_end", "flow_event", "o2_basis", "source_id"):
                    _add_numbers(bag, Counter(by_id[i].get(key) for i in group).values())
                _add_numbers(bag, Counter(_diluent(by_id[i]) for i in group).values())
                _add_numbers(bag, [len(group), len({by_id[i]["investigation_id"] for i in group})])
                for var in ("o2_pct", "pressure_kpa", "co2_pct", "he_pct", "flow_cms"):
                    _add_numbers(bag, [sum(_num(by_id[i].get(var)) is None for i in group)])
            out_ids = outside.get(need, set())
            _add_numbers(bag, [len(out_ids), len({by_id[i]["investigation_id"] for i in out_ids if i in by_id})])
            _add_numbers(bag, Counter(by_id[i]["investigation_id"] for i in out_ids if i in by_id).values())
            _add_numbers(bag, [len(ids), row["tests_recorded_outside_objective"],
                               sum(mk[i]["flow"] == "in" for i in best),
                               sum(mk[i]["flow"] == "not_recorded" for i in best),
                               sum(mk[i]["gravity"] == "same" for i in best)])
            rows[(sid, need)] = row
        # per investigation, for the result notes
        per_inv = defaultdict(list)
        for t in tests:
            per_inv[t["investigation_id"]].append(t)
        for inv, ts in per_inv.items():
            b = bag_inv[(sid, inv)]
            amb = [t for t in ts if t.get("o2_basis") == "ambient"]
            _add_numbers(b, [len(ts), len(amb), sum(t.get("o2_basis") == "oxidizer_stream" for t in ts)])
            _add_numbers(b, Counter(mk[t["test_id"]]["tier"] for t in ts).values())
            _add_numbers(b, Counter(mk[t["test_id"]]["tier"] for t in amb).values())
            _add_numbers(b, Counter(t.get("source_id") for t in ts).values())
            for var in ("o2_pct", "pressure_kpa"):
                _add_numbers(b, [sum(_num(t.get(var)) is None for t in ts)])

    # global anchors and facts shared by every statement
    solid = [t for t in tests if t.get("fuel_phase") == "solid"]
    amb_o2 = [_num(t["o2_pct"]) for t in tests if t.get("o2_basis") == "ambient" and _num(t.get("o2_pct")) is not None]
    stream_o2 = [_num(t["o2_pct"]) for t in tests
                 if t.get("o2_basis") == "oxidizer_stream" and _num(t.get("o2_pct")) is not None]
    solid_o2 = [_num(t["o2_pct"]) for t in solid if _num(t.get("o2_pct")) is not None]
    anchors = {
        "solid_tests": len(solid),
        "solid_tests_with_pressure": sum(_num(t.get("pressure_kpa")) is not None for t in solid),
        "highest_solid_o2": max(solid_o2) if solid_o2 else None,
        "highest_ambient_o2": max(amb_o2) if amb_o2 else None,
        "highest_stream_o2": max(stream_o2) if stream_o2 else None,
    }

    def tier_ids(sid, need, tier):
        return [i for i in usable.get(need, set()) if marks.get(sid, {}).get(i, {}).get("tier") == tier]
    if "lunar_habitat" in marks:
        lun = [by_id[i] for i in tier_ids("lunar_habitat", "S1", "atmosphere")]
        anchors["lunar_S1_in_bins"] = len(lun)
        anchors["lunar_S1_in_bins_investigations"] = sorted({t["investigation_id"] for t in lun})
        anchors["lunar_S1_in_bins_balance"] = dict(Counter(_diluent(t) for t in lun))
        anchors["lunar_S1_in_bins_test_end"] = dict(Counter(t.get("test_end") or "not recorded" for t in lun))
    if "iss" in marks:
        iss = [by_id[i] for i in tier_ids("iss", "S1", "atmosphere")]
        anchors["iss_S1_in_bins"] = len(iss)
        anchors["iss_S1_in_bins_diluted"] = sum(_diluent(t) not in ("n2_only", "not_recorded") for t in iss)
        anchors["iss_P1_oxygen_only"] = len(tier_ids("iss", "P1", "oxygen_only"))
    in_bins_basis = Counter(by_id[i].get("o2_basis") for (sid, need) in rows
                            for i in tier_ids(sid, need, "atmosphere") + tier_ids(sid, need, "oxygen_only"))
    anchors["in_bin_basis"] = dict(in_bins_basis)

    bag_global = set()
    _add_numbers(bag_global, [len(tests), len(solid), anchors["solid_tests_with_pressure"],
                              anchors["highest_solid_o2"], anchors["highest_ambient_o2"],
                              anchors["highest_stream_o2"], len({t["investigation_id"] for t in tests}),
                              len(list(config.PSI_CATALOG_DIR.glob("PSI-*.json"))), len(sources), len(needs)])
    _add_numbers(bag_global, Counter(t["investigation_id"] for t in tests).values())
    _add_numbers(bag_global, Counter(t["source_id"] for t in tests).values())
    _add_numbers(bag_global, Counter(t.get("o2_basis") for t in tests).values())
    _add_numbers(bag_global, Counter((t.get("fuel_phase"), t.get("o2_basis")) for t in tests).values())
    table_bags = defaultdict(set)
    for s in sources:
        if s.get("row_unit") != "test":
            table_bags[s["investigation_id"]] |= _psi_table_numbers(s["file"])
    return {"rows": rows, "anchors": anchors, "bag_need": bag_need, "bag_inv": bag_inv, "bag_scen": bag_scen,
            "bag_global": bag_global, "table_bags": table_bags, "needs": needs, "sources": sources,
            "scenario_ids": [s["id"] for s in spec["scenarios"]]}


# Anchors the wording rests on. The rules below are stated by the text and must hold whatever the data;
# the counts are not hard-coded (they moved with the data role's audit: 1,867 -> 1,824 test rows, 377 ->
# 376 solid tests, ISS P1 oxygen-only 55 -> 58) but compared with a third code path, the data role's
# evidence packages and investigation_facts.json, which ai/check_all.py does not use for the recount.
EXPECTED_ANCHORS = {
    "solid_tests_with_pressure": 0,                    # 'pressure is not a column in any solid-sample table'
    "lunar_S1_in_bins_investigations": ["PSI-69"],     # 'all fuel-droplet tests (PSI-69 (FLEX))'
}


def third_path_anchors():
    """The same anchors from data/pipeline/evidence/scenario_*.json and data/pipeline/investigation_facts.json."""
    out = {}
    facts = json.loads((PIPE / "investigation_facts.json").read_text(encoding="utf-8"))
    solid = [t for i in facts["investigations"] for t in i.get("tables", [])
             if (t.get("constants") or {}).get("fuel_phase") == "solid"]
    out["solid_tests"] = sum(t.get("tests") or 0 for t in solid)
    out["solid_tests_with_pressure"] = sum(((t.get("variables") or {}).get("pressure_kpa") or {}).get("n") or 0
                                           for t in solid)
    mx = [((t.get("variables") or {}).get("o2_pct") or {}).get("max") for t in solid]
    out["highest_solid_o2"] = max(x for x in mx if x is not None)

    def need(sid, nid):
        p = PIPE / "evidence" / f"scenario_{sid}.json"
        if not p.exists():
            return None
        doc = json.loads(p.read_text(encoding="utf-8"))
        return next((n for n in doc["needs"] if n["need_id"] == nid), None)
    lun, iss, p1 = need("lunar_habitat", "S1"), need("iss", "S1"), need("iss", "P1")
    if lun:
        atm = [m for m in lun["matched_tests"] if m["tier"] == "atmosphere"]
        out["lunar_S1_in_bins"] = lun["counts"]["atmosphere"]
        out["lunar_S1_in_bins_investigations"] = sorted({m["investigation_id"] for m in atm})
        out["lunar_S1_in_bins_test_end"] = dict(Counter((m["values"].get("test_end") or {}).get("value")
                                                        or "not recorded" for m in atm))
    if iss:
        atm = [m for m in iss["matched_tests"] if m["tier"] == "atmosphere"]
        out["iss_S1_in_bins"] = iss["counts"]["atmosphere"]
        out["iss_S1_in_bins_diluted"] = sum(m["added_gas"] == "co2_or_helium" for m in atm)
    if p1:
        out["iss_P1_oxygen_only"] = p1["counts"]["oxygen_only"]
    return out


def check_codes(rep, rows):
    bad = []
    for r in rows:
        if r.get("status") not in STATUSES:
            bad.append(f"{r.get('scenario_id')}/{r.get('need_id')}: unknown status {r.get('status')!r}")
        for g in [x for x in (r.get("gaps") or "").split(";") if x]:
            if g not in GAP_CODES:
                bad.append(f"{r.get('scenario_id')}/{r.get('need_id')}: unknown gap code {g!r}")
    for b in bad:
        rep.fail("codes", b)
    if not bad:
        rep.ok("codes", f"{len(rows)} scenario_needs.csv rows use only the {len(STATUSES)} known statuses and "
                        f"{len(GAP_CODES)} known gap codes")


def check_recount(rep, rc):
    sn = _read_csv(PIPE / "scenario_needs.csv")
    check_codes(rep, sn)
    before, n = len(rep.failures()), 0
    for r in sn:
        key = (r["scenario_id"], r["need_id"])
        mine = rc["rows"].get(key)
        if mine is None:
            rep.fail("recount", f"{key}: row in scenario_needs.csv but not in the recount (spec changed?)")
            continue
        n += 1
        for col in ["usable_tests", "tests_recorded_outside_objective"] + [f"tests_{t}" for t in TIERS]:
            if int(r[col]) != mine[col]:
                rep.fail("recount", f"{key} {col}: scenario_needs.csv {r[col]}, recount {mine[col]}")
        for t in TIERS:
            if (r[f"investigations_{t}"] or "") != mine[f"investigations_{t}"]:
                rep.fail("recount", f"{key} investigations_{t}: {r[f'investigations_{t}']!r} vs {mine[f'investigations_{t}']!r}")
    a = rc["anchors"]
    for k, want in EXPECTED_ANCHORS.items():
        if a.get(k) != want:
            rep.fail("recount", f"anchor {k}: expected {want}, recount {a.get(k)}")
    try:
        third = third_path_anchors()
    except (OSError, KeyError, ValueError) as exc:
        rep.fail("recount", f"third path (evidence packages, investigation_facts.json) could not be read: {exc}")
        third = {}
    for k, want in third.items():
        if a.get(k) != want:
            rep.fail("recount", f"anchor {k}: evidence packages / investigation_facts.json {want}, recount {a.get(k)}")
    lun = a.get("lunar_S1_in_bins_test_end", {})
    if lun.get("extinction"):
        rep.fail("recount", f"anchor: lunar S1 in-bin tests include {lun['extinction']} recorded extinctions")
    basis = a.get("in_bin_basis", {})
    if set(basis) - {"ambient"}:
        rep.fail("recount", f"anchor: tests counted inside the bins have non-ambient oxygen basis: {basis}")
    if len(rep.failures()) == before:
        rep.ok("recount", f"{n} scenario/need rows of scenario_needs.csv equal the second-path recount "
                          f"(usable, outside objective, four tiers, investigations); {len(third)} anchors equal "
                          "the third path (evidence packages, investigation_facts.json)")
    rep.info("recount", "anchors: " + json.dumps({k: a[k] for k in a}, sort_keys=True))


# ====================================================================== cards

CARD_FIELDS = ("investigation_id", "summary", "key_points", "ai_generated", "model", "reviewed_by", "updated")


def _ws(text):
    return re.sub(r"\s+", " ", text or "").strip()


_LABEL_FIELD = {v[1]: f for f, v in evmod.FIELDS.items()}


def _label_quote(text):
    """'Stated objective: "..."' -> ('Stated objective:', '...') or (None, None)."""
    for label in _LABEL_FIELD:
        if text.startswith(label + ' "') and text.endswith('"'):
            return label, text[len(label) + 2:-1]
    return None, None


def _quoted_segments(summary):
    """Every '"<text>"' in a summary string with the field label written before it
    ('Stated objective: "a" "b"' gives two segments with the same label)."""
    out = []
    for m in re.finditer(r'"([^"]+)"', summary):
        before = summary[:m.start()]
        label = max(_LABEL_FIELD, key=lambda lb: before.rfind(lb))
        out.append((label if before.rfind(label) >= 0 else None, m.group(1)))
    return out


def _field_text(inv, field):
    try:
        return resolve.resolve(f"{inv}.{field}")["text"]
    except (resolve.SourceNotFound, resolve.BadSource):
        return ""


def _verbatim(inv, label, text, ev):
    """The unit(s) of the labelled field that a quoted span covers, or None if the span is not
    verbatim. Verbatim means: equal to a piece of the PSI field with runs of whitespace shown as one
    space, starting at a unit start and ending at a unit end."""
    field = _LABEL_FIELD.get(label)
    if not field or not text:
        return None
    raw = _field_text(inv, field)
    us = [u for u in evmod.record(inv, ev)["units"] if u["field"] == field]
    want = _ws(text)
    for a in us:
        starts = {a["char_start"]}
        if a.get("list_marker"):  # a span may start at the list marker before the unit ('1. Plan ...')
            k = raw.rfind(a["list_marker"], 0, a["char_start"])
            if k >= 0 and not raw[k + len(a["list_marker"]):a["char_start"]].strip():
                starts.add(k)
        for st in starts:
            for b in us:
                if b["char_end"] > st and _ws(raw[st:b["char_end"]]) == want:
                    return [u for u in us if st <= u["char_start"] < b["char_end"]]
    return None


def _walk_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}", k
            yield from _walk_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_keys(v, f"{path}[{i}]")


def check_evidence_quotes(rep, inv, s, ev, sec="cards"):
    """Every stored evidence quote is the exact text of its unit (taken by code), and its offsets
    reproduce it in the record field."""
    for e in s.get("evidence") or []:
        try:
            u = evmod.unit(inv, e.get("id"), ev)
        except KeyError:
            rep.fail(sec, f"{inv}: evidence id {e.get('id')} is not a unit of evidence.json")
            continue
        q = e.get("quote") or ""
        if q not in u["text"] or q != u["text"]:
            rep.fail(sec, f"{inv} {u['id']}: stored evidence quote is not the exact unit text: {q[:70]!r}")
        if "char_start" in e and _field_text(inv, u["field"])[e["char_start"]:e.get("char_end")] != q:
            rep.fail(sec, f"{inv} {u['id']}: evidence offsets do not reproduce the stored quote")


def _prereview():
    from ai import apply_cards
    try:
        return apply_cards.load_prereview()
    except SystemExit as exc:
        return exc


def check_card(rep, card, ev, final=False, prereview=()):
    inv = card.get("investigation_id")
    sec = "cards"
    missing = [k for k in CARD_FIELDS if k not in card]
    if missing:
        rep.fail(sec, f"{inv}: missing contract fields {', '.join(missing)}")
    if inv not in ev["records"]:
        rep.fail(sec, f"{inv}: not a record in evidence.json")
        return
    kps = card.get("key_points") or []
    if len(kps) > 4:
        rep.fail(sec, f"{inv}: {len(kps)} key points, at most 4")
    kp_units = []
    for kp in kps:
        label, q = _label_quote(kp.get("text") or "")
        used = _verbatim(inv, label, q, ev) if label else None
        if not used:
            rep.fail(sec, f"{inv}: key point is not '<field label> \"<verbatim PSI text>\"': {kp.get('text', '')[:80]!r}")
            continue
        if kp.get("source") != used[-1]["source"]:
            rep.fail(sec, f"{inv}: key point source {kp.get('source')} != {used[-1]['source']}")
        kp_units += [u["id"] for u in used]
    for s in card.get("summary_sources") or []:
        if not resolve.check(s):
            rep.fail(sec, f"{inv}: summary_sources entry {s!r} does not resolve")
    sents = card.get("sentences") or []
    model_sents = [s for s in sents if s.get("origin") == "model"]
    for s in sents:
        check_evidence_quotes(rep, inv, s, ev, sec)
    if bool(card.get("ai_generated")) != bool(model_sents):
        rep.fail(sec, f"{inv}: ai_generated is {card.get('ai_generated')!r} with {len(model_sents)} model sentence(s) "
                      "shown (true exactly when a model sentence is shown)")
    for e in prereview:
        if e["investigation_id"] != inv:
            continue
        for s in model_sents:
            body, _, _ = C.split_source_suffix(s.get("text") or "")
            if e["sentence"].strip() in ((s.get("text") or "").strip(), body.strip()):
                rep.fail(sec, f"{inv}: a sentence listed in ai/review/pm_prereview.json remains: {body[:80]!r}")
    for x in card.get("removed_before_review") or []:
        if card.get("status") != "generated_partial" and model_sents:
            rep.fail(sec, f"{inv}: a sentence was removed before review but status is {card.get('status')!r}")
    slots = [s for s in sents if s.get("origin") == "quote" and s.get("role") == "summary" and s.get("replaces")]
    for s in slots:
        if f'{s.get("field_label")} "{s.get("text")}"' not in (card.get("summary") or ""):
            rep.fail(sec, f"{inv}: the quoted slot of removed sentence {s['replaces'].get('n')} is not in the summary")
    if slots and card.get("reviewed_by") and any(not x.get("review") for x in model_sents):
        rep.fail(sec, f"{inv}: reviewed_by set by a reviewed removal")
    summary_model = [s for s in model_sents if s.get("role") == "summary"]
    status = card.get("status")
    if status is not None and status not in ("generated", "generated_partial", "fallback_quote"):
        rep.fail(sec, f"{inv}: unknown status {status!r}")
    if status == "fallback_quote" and model_sents:
        rep.fail(sec, f"{inv}: status fallback_quote but {len(model_sents)} model sentence(s)")
    if model_sents:
        if not card.get("ai_generated"):
            rep.fail(sec, f"{inv}: has model sentences but ai_generated is not true")
        if config.MODEL not in str(card.get("model")):
            rep.fail(sec, f"{inv}: has model sentences but model is {card.get('model')!r}")
    if not summary_model:
        # a quoted summary: every quoted segment is a verbatim unit with its field label
        summ = card.get("summary") or ""
        segs = _quoted_segments(summ)
        if not segs:
            rep.fail(sec, f"{inv}: summary has no model sentence and no labelled quote: {summ[:80]!r}")
        for label, q in segs:
            if not _verbatim(inv, label, q, ev):
                rep.fail(sec, f"{inv}: quoted summary segment is not a verbatim unit: {label} {q[:60]!r}")
    for s in sents:
        if s.get("origin") == "quote":
            label = s.get("field_label")
            t = s.get("text") or ""
            lq, q = _label_quote(t)
            used = _verbatim(inv, lq or label, q if lq else t, ev)
            if not used:
                rep.fail(sec, f"{inv}: quote sentence is not verbatim PSI text with its field label: {t[:80]!r}")
            elif "char_start" in s and "source" in s:
                fld = str(s["source"]).split(".", 1)[-1]
                if _ws(_field_text(inv, fld)[s["char_start"]:s.get("char_end")]) != _ws(q if lq else t):
                    rep.fail(sec, f"{inv}: quote sentence offsets do not reproduce its text")
            continue
        if s.get("origin") != "model":
            rep.fail(sec, f"{inv}: sentence origin {s.get('origin')!r}")
            continue
        text = s.get("text") or ""
        body, suffix_inv, fields = C.split_source_suffix(text)
        gate_ev = [{"id": e.get("id"), "quote": e.get("model_quote", e.get("quote")), "source": e.get("source"),
                    "char_start": e.get("char_start"), "char_end": e.get("char_end")} for e in s.get("evidence") or []]
        res = C.check_sentence(body, gate_ev, inv, ev, n_summary=len(summary_model))
        if not res["ok"]:
            rep.fail(sec, f"{inv}: model sentence fails: {'; '.join(res['reasons'])} :: {body[:90]!r}")
        stored = s.get("checks") or {}
        diff = {k: (stored.get(k), v) for k, v in res["checks"].items() if k in stored and stored[k] != v}
        if diff:
            rep.fail(sec, f"{inv}: stored checks differ from a fresh run: {diff}")
        if s.get("role") == "summary":
            cited_fields = sorted({evmod.unit(inv, e["id"], ev)["field"] for e in s.get("evidence") or []
                                   if res["checks"]["ids_ok"]})
            if suffix_inv != inv:
                rep.fail(sec, f"{inv}: model summary sentence does not end with '({inv} record: <field>)'")
            elif sorted(fields) != cited_fields:
                rep.fail(sec, f"{inv}: bracketed source names {fields}, cited units are {cited_fields}")
            first = (s.get("evidence") or [{}])[0].get("id")
            hidden_units = {u for h in card.get("hidden_by_review") or [] if h.get("role") == "key_point"
                            for u in h.get("unit_ids") or []}
            if first not in kp_units and first not in hidden_units:
                rep.fail(sec, f"{inv}: first cited unit {first} is not among the key points")
            if text not in (card.get("summary") or ""):
                rep.fail(sec, f"{inv}: model summary sentence is not in the card's summary string")
        rv = s.get("review")
        if rv:
            if rv.get("verdict") in VERDICT_REMOVE:
                rep.fail(sec, f"{inv}: a sentence with review verdict {rv.get('verdict')!r} remains")
            if rv.get("modality_kept") == "no":
                rep.fail(sec, f"{inv}: a sentence with modality_kept 'no' remains")
        elif final:
            rep.fail(sec, f"{inv}: unreviewed model sentence remains (--final)")
    if card.get("reviewed_by") and any(not s.get("review") for s in model_sents):
        rep.fail(sec, f"{inv}: reviewed_by is set but not every model sentence has a review")
    shown_items = {apply_cards_quote_item(inv, s) for s in sents if s.get("origin") == "quote"}
    for h in card.get("hidden_by_review") or []:
        if h.get("item") in shown_items:
            rep.fail(sec, f"{inv}: {h.get('item')} is listed under hidden_by_review but is shown")


def apply_cards_quote_item(inv, s):
    from ai import apply_cards
    return apply_cards.quote_item(inv, s)


def check_sheet(rep, cards_path, scenarios_path, ev):
    """The review sheet lists what the page shows: every shown card sentence and scenario statement has a row
    with shown = yes, no row with shown = yes is missing from the page, and no row whose verdict removes its
    sentence is shown (ai/apply_review.py refresh_sheet; independent check of 14 Nov 17:10)."""
    from ai import apply_review
    sec = "sheet"
    sheet = apply_review.SHEET
    if not sheet.exists() or not Path(cards_path).exists():
        rep.not_built(sec, f"{_rel(sheet)}: not built yet")
        return
    before = len(rep.failures())
    rows = apply_review.read_sheet(sheet)
    if rows and "shown" not in rows[0]:
        rep.fail(sec, f"{_rel(sheet)} has no 'shown' column; rebuild with python3 ai/build_all.py")
        return
    cards = json.loads(Path(cards_path).read_text(encoding="utf-8"))
    scen = json.loads(Path(scenarios_path).read_text(encoding="utf-8")) if Path(scenarios_path).exists() else []
    model, quotes = apply_review.card_rows(cards, ev)
    page = {(r["item"], r["sentence_sha"]) for r in model + quotes + apply_review.template_rows(scen)}
    shown = {(r["item"], r["sentence_sha"]) for r in rows if r.get("shown") == "yes"}
    keys = [(r["item"], r["sentence_sha"]) for r in rows]
    for k in sorted(page - shown):
        rep.fail(sec, f"shown on the page but no row with shown = yes: {k[0]} ({k[1]})")
    for k in sorted(shown - page):
        rep.fail(sec, f"row with shown = yes that the page does not show: {k[0]} ({k[1]})")
    dup = [k for k, n in Counter(keys).items() if n > 1]
    if dup:
        rep.fail(sec, f"{len(dup)} duplicate row(s): {dup[:3]}")
    one_summary = {c["investigation_id"] for c in cards
                   if sum(s.get("role") == "summary" for s in c.get("sentences") or []) == 1}
    for r in rows:
        v = (r.get("verdict") or "").strip()
        removing = ((r["origin"] == "model" and (v in VERDICT_REMOVE or (r.get("modality_kept") or "").strip() == "no"))
                    or (r["origin"] == "quote" and v == "not_relevant"))
        if r.get("shown") == "yes" and removing:
            inv = r["item"].split(":")[1]
            last = r["origin"] == "quote" and r["role"] == "summary" and inv in one_summary
            if last:
                rep.info(sec, f"{r['item']} is marked not_relevant and stays as the card's last summary quote")
            else:
                rep.fail(sec, f"{r['item']}: verdict {v!r} but shown = yes")
        if r.get("shown") == "no" and not removing and r["origin"] != "model":
            rep.fail(sec, f"{r['item']}: shown = no without a verdict that removes it")
    n_no = sum(r.get("shown") == "no" for r in rows)
    if len(rep.failures()) == before:
        rep.ok(sec, f"{len(rows)} rows: {len(shown)} shown (= every sentence the cards and scenarios show), {n_no} not "
                    f"shown because of a verdict or --final; {sum(not (r.get('verdict') or '').strip() for r in rows)} "
                    "row(s) without a verdict")


def check_cards(rep, path, ev, final=False):
    path = Path(path)
    if not path.exists():
        rep.not_built("cards", f"{_rel(path)}: not built yet")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        rep.fail("cards", "cards.json is not an array (the page requires an array)")
        return
    before = len(rep.failures())
    ids = [c.get("investigation_id") for c in data]
    if len(data) != len(ev["records"]) or set(ids) != set(ev["records"]) or len(set(ids)) != len(ids):
        rep.fail("cards", f"{len(data)} cards for {len(set(ids))} investigations; expected one per each of "
                          f"the {len(ev['records'])} records")
    for p, k in _walk_keys(data):
        if FORBIDDEN_SCORE_KEYS.search(k):
            rep.fail("cards", f"cards.json carries a fact-check-model field {p} (design: never in product data)")
    pre = _prereview()
    if isinstance(pre, SystemExit):
        rep.fail("cards", f"ai/review/pm_prereview.json: {pre}")
        pre = []
    for c in data:
        check_card(rep, c, ev, final=final, prereview=pre)
    model_n = sum(s.get("origin") == "model" for c in data for s in c.get("sentences") or [])
    by_status = Counter(c.get("status") for c in data)
    n_ev = sum(len(s.get("evidence") or []) for c in data for s in c.get("sentences") or [])
    n_pre = sum(len(c.get("removed_before_review") or []) for c in data)
    n_slot = sum(1 for c in data for x in c.get("removed_before_review") or [] if x.get("replaced_by"))
    n_hid = sum(len(c.get("hidden_by_review") or []) for c in data)
    if len(rep.failures()) == before:
        rep.ok("cards", f"{len(data)} cards pass; {model_n} model sentence(s) re-gated; {n_ev} stored evidence quotes "
                        f"equal their unit; {n_pre} sentence(s) removed before review, {n_slot} of them shown as quoted "
                        f"slots; {n_hid} quote(s) marked not_relevant not shown; "
                        f"status {dict(by_status)}")
    else:
        rep.info("cards", f"{model_n} model sentence(s); status {dict(by_status)}")


# ====================================================================== scenarios

def _hash_candidates(paths):
    files = [ROOT / p for p in paths]
    if not all(f.exists() for f in files):
        return set()
    shas = {p: metamod.sha256_file(ROOT / p) for p in paths}
    out = {metamod.sha256_json(shas), metamod.sha256_json(dict(sorted(shas.items())))}
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update((ROOT / p).read_bytes())
    out.add(h.hexdigest())
    out.add(hashlib.sha256("\n".join(shas[p] for p in sorted(paths)).encode()).hexdigest())
    out.add(hashlib.sha256("".join(shas[p] for p in sorted(paths)).encode()).hexdigest())
    return out


def _scenario_inputs():
    from ai import build_baseline
    return build_baseline.scenario_inputs()


SCENARIO_INPUTS = _scenario_inputs()
CATALOG_INPUTS = ["data/catalog/configurations.csv", "data/catalog/investigations.csv"]


def _check_fresh(rep, sid, fresh):
    sec = "scenarios"
    if not isinstance(fresh, dict):
        rep.fail(sec, f"{sid}: no fresh{{}} block")
        return
    cfg_path = ROOT / "scoring" / "scoring_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if str(fresh.get("ranker_config_version")) != str(cfg.get("version")):
        rep.fail(sec, f"{sid}: ranker_config_version {fresh.get('ranker_config_version')} != {cfg.get('version')}")
    for key, paths in (("scoring_config_sha256", ["scoring/scoring_config.json"]),
                       ("catalog_sha256", CATALOG_INPUTS), ("scenario_inputs_sha256", SCENARIO_INPUTS)):
        stored = fresh.get(key)
        if isinstance(stored, dict):
            stale = [p for p, sha in stored.items() if not (ROOT / p).exists() or metamod.sha256_file(ROOT / p) != sha]
            if stale:
                rep.fail(sec, f"{sid}: {key} stale for {', '.join(stale)}")
        elif isinstance(stored, str):
            cands = _hash_candidates(paths) | ({metamod.sha256_file(ROOT / paths[0])} if len(paths) == 1 else set())
            if stored not in cands:
                rep.fail(sec, f"{sid}: {key} does not match the current files ({', '.join(paths)}) under any "
                              "hash definition check_all knows; stale, or store it as {path: sha256}")
        else:
            rep.fail(sec, f"{sid}: fresh.{key} missing")


def _live_note_ids(query):
    from scoring import scorer  # imported, unchanged (owned by ui)
    r = scorer.rank(query)
    res = r.get("results") or []
    top = [x["psi_accession"] for x in res[:3]]
    ids = set(top)
    if len(res) >= 3:
        s3 = res[2]["score"]
        ids |= {x["psi_accession"] for x in r.get("ranking") or []
                if x.get("score") is not None and round(abs(x["score"] - s3), 1) < NEAR_TIE_POINTS}
    return ids, top, r


def _ref_value_numbers(data):
    """Numbers of a resolved references.json item's machine-readable values, and its row count."""
    value = (data or {}).get("value")
    out = set()
    if isinstance(value, dict):  # the item's own text (its 'quote' is what resolve() returns as text)
        for k in ("text", "quote"):
            if isinstance(value.get(k), str):
                out |= {round(float(n["value"]), 6) for n in C.extract_numbers(value[k])}
    if isinstance(value, dict) and isinstance(value.get("values"), dict):
        vals = value["values"]
        out |= {round(v, 6) for v in C._facts_numbers(vals)}
        for v in vals.values():
            if isinstance(v, list):
                out.add(float(len(v)))
    return out


def _facts_found(facts, bags, sources):
    """Facts numbers not found in any bag nor as a numeral (or a machine-readable value) of a cited source."""
    vals = C._facts_numbers(facts or {})
    pool = set().union(*bags) if bags else set()
    src_nums, src_psi = set(), set()
    for s in sources or []:
        try:
            r = resolve.resolve(s)
            nums = C.extract_numbers(r["text"])
            src_nums |= _ref_value_numbers(r.get("data"))
            # number words of a cited fixed sentence ('one of the two ranges') are the source's wording
            src_nums |= {float(LP_NUMBER_WORDS[w]) for w in C.number_words(r["text"]) if w in LP_NUMBER_WORDS}
        except (resolve.SourceNotFound, resolve.BadSource):
            continue
        src_nums |= {round(float(n["value"]), 6) for n in nums}
        src_psi |= {float(n["value"]) for n in nums if n["unit"] in ("psi", "psia")}
    missing, by_src = [], 0
    for v in vals:
        r = round(v, 6)
        if r in pool:
            continue
        if r in src_nums or r in CONSTANTS:
            by_src += 1
            continue
        if any(abs(round(x * f, d) - v) < 1e-9 for x in src_psi for f in (CONSTANTS_PSI_KPA,) for d in (1, 2)):
            by_src += 1  # a psi value of a cited source written in kPa by code (1 psi = 6.894757 kPa)
            continue
        if any(abs(round(x, d) - v) < 1e-9 for x in src_nums for d in (0, 1)):
            by_src += 1  # a value of a cited source rounded by code to whole units or 0.1 ('71 to 72 kPa')
            continue
        missing.append(v)
    return missing, len(vals), by_src


PIPELINE_SENTENCES = "data/pipeline/evidence/"


def _check_statement(rep, where, item, text_key, bags, extra_sources=()):
    text = item.get(text_key) or ""
    sources = list(item.get("sources") or []) + list(extra_sources)
    if item.get("text_origin") != "template":
        rep.fail("scenarios", f"{where}: text_origin is {item.get('text_origin')!r}, not 'template' (code-built text)")
    for s in sources:
        if s.startswith(PIPELINE_SENTENCES) and "#" in s and resolve.check(s):
            r = resolve.resolve(s)
            value = (r.get("data") or {}).get("value")
            # a fixed sentence (a string, or a statement object with its text) must be in the text as written; a
            # structured value of a package (matched_ranges) is cited for its numbers, checked with the facts
            if not (isinstance(value, str) or (isinstance(value, dict) and isinstance(value.get("text"), str))):
                continue
            fixed = r["text"]
            if C._norm_quote(fixed) not in C._norm_quote(text) and fixed.rstrip(". ") not in text:
                rep.fail("scenarios", f"{where}: cites the pipeline sentence {s} but does not contain it as written")
    res = C.check_template(text, item.get("facts") or {}, sources)
    if not res["ok"]:
        rep.fail("scenarios", f"{where}: {'; '.join(res['reasons'])} :: {text[:100]!r}")
    for s in sources:
        if not resolve.check(s):
            rep.fail("scenarios", f"{where}: source {s!r} does not resolve")
    if item.get("needed_data"):
        r2 = C.check_template(item["needed_data"], item.get("facts") or {}, ())
        if not r2["ok"]:
            rep.fail("scenarios", f"{where} needed_data: {'; '.join(r2['reasons'])}")
    missing, n, by_src = _facts_found(item.get("facts"), bags, sources)
    if missing:
        rep.fail("scenarios", f"{where}: facts value(s) {missing} not found by the recount or in a cited source")
    return n, by_src


def check_scenarios(rep, path, ev, recount=None, live_rank=True):
    path = Path(path)
    sec = "scenarios"
    if not path.exists():
        rep.not_built(sec, f"{_rel(path)}: not built yet")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        rep.fail(sec, "scenarios.json is not an array (the page requires an array)")
        return
    rc = recount or globals()["recount"]()
    before = len(rep.failures())
    want = dict(QUERIES)
    got = {e.get("id"): e for e in data}
    for sid in got:
        if sid not in want:
            rep.fail(sec, f"entry {sid!r} is not one of the contract queries {list(want)}")
    for sid in want:
        if sid not in got:
            rep.info(sec, f"{sid}: no entry yet")
    no_table = {s["investigation_id"] for s in rc["sources"]}
    n_facts = n_src = n_items = 0
    for sid, e in got.items():
        if sid not in want:
            continue
        if e.get("query") != want[sid]:
            rep.fail(sec, f"{sid}: query {e.get('query')!r} != {want[sid]!r}")
        if e.get("ranking_source") != "scoring.scorer.rank":
            rep.fail(sec, f"{sid}: ranking_source {e.get('ranking_source')!r}")
        # the page tags text_origin 'template' as 'Computed by team code from NASA PSI tables' and anything
        # else as AI-generated; the entry is code-built, so it says so (the code's own AI authorship is in _meta)
        for k in ("text_origin", "frame_text_origin"):
            if e.get(k) != "template":
                rep.fail(sec, f"{sid}: {k} is {e.get(k)!r}, not 'template'")
        if e.get("ai_generated") is not False:
            rep.fail(sec, f"{sid}: ai_generated is {e.get('ai_generated')!r}; a code-built entry says false")
        bag_all_needs = set().union(*[rc["bag_need"][(sid, n)] for n in rc["needs"]]) if sid in rc["scenario_ids"] else set()
        scen = [rc["bag_scen"].get(sid, set()), rc["bag_global"]]
        if e.get("frame"):
            a, b = _check_statement(rep, f"{sid} frame", {"text": e["frame"], "facts": e.get("frame_facts") or e.get("facts") or {},
                                                          "sources": e.get("frame_sources") or [],
                                                          "text_origin": e.get("frame_text_origin")},
                                    "text", scen + [bag_all_needs])
            n_facts, n_src, n_items = n_facts + a, n_src + b, n_items + 1
        need_ids = [x.get("need_id") for x in e.get("needs") or []]
        if sorted(need_ids) != sorted(rc["needs"]) or len(set(need_ids)) != len(need_ids):
            rep.fail(sec, f"{sid}: need entries {need_ids} != need ids in needs.json {rc['needs']}")
        for x in e.get("needs") or []:
            a, b = _check_statement(rep, f"{sid} need {x.get('need_id')}", x, "statement",
                                    scen + [rc["bag_need"].get((sid, x.get("need_id")), set())])
            n_facts, n_src, n_items = n_facts + a, n_src + b, n_items + 1
            # the need's reading is the data role's text, used as written; a reading that says no test is counted
            # next to a count above zero is reported (not a pm failure: the fix is in pipeline/spec/needs.json)
            reading = (x.get("statement") or "").split(T.READING_LEAD)[-1]
            if (x.get("facts") or {}).get("usable_tests") and re.search(r"\bno test is counted\b", reading, re.I):
                rep.info(sec, f"{sid} need {x.get('need_id')}: the pipeline's reading says no test is counted next to "
                              f"{x['facts']['usable_tests']} counted tests (data role's text in pipeline/spec/needs.json)")
        for i, x in enumerate(e.get("gaps") or []):
            a, b = _check_statement(rep, f"{sid} gap {i + 1}", x, "text",
                                    scen + [bag_all_needs] + list(rc["table_bags"].values()))
            n_facts, n_src, n_items = n_facts + a, n_src + b, n_items + 1
        notes = e.get("result_notes") or []
        for x in notes:
            inv = x.get("investigation_id")
            a, b = _check_statement(rep, f"{sid} note {inv}", x, "text",
                                    scen + [rc["bag_inv"].get((sid, inv), set()), rc["table_bags"].get(inv, set())])
            n_facts, n_src, n_items = n_facts + a, n_src + b, n_items + 1
            if NO_TABLE_PHRASE.lower() in (x.get("text") or "").lower() and inv in no_table:
                rep.fail(sec, f"{sid} note {inv}: says '{NO_TABLE_PHRASE}' but sources.json has an entry for it")
        if live_rank:
            try:
                live, top, _ = _live_note_ids(want[sid])
                noted = {x.get("investigation_id") for x in notes}
                if noted != live:
                    rep.fail(sec, f"{sid}: note ids {sorted(noted, key=_acc_key)} != live top 3 plus near-ties "
                                  f"{sorted(live, key=_acc_key)} (top 3 {top})")
            except Exception as exc:
                rep.fail(sec, f"{sid}: rank({want[sid]!r}) raised {type(exc).__name__}: {exc}")
        _check_fresh(rep, sid, e.get("fresh"))
    if len(rep.failures()) == before:
        rep.ok(sec, f"{len(got)} scenario entries, {n_items} statements pass the template checks; "
                    f"{n_facts} facts values recounted ({n_src} of them found in a cited source)")
    else:
        rep.info(sec, f"{n_items} statements, {n_facts} facts values checked ({n_src} via a cited source)")


# ====================================================================== components J and K

def check_readiness_and_robustness(rep):
    """model_readiness.json equals a fresh build (ai/model_readiness.py check) and robustness.json is current
    against rank() now (ai/robustness.py check_file, NumPy path only). Both need NumPy (and scikit-learn for
    the readiness rebuild); without them the check fails, it does not skip."""
    try:
        from ai import model_readiness
        model_readiness.check(rep)
    except ImportError as exc:
        rep.fail("model_readiness", f"cannot import ai/model_readiness.py: {exc}")
    try:
        from ai import robustness
        robustness.check_file(rep)
    except ImportError as exc:
        rep.fail("robustness", f"cannot import ai/robustness.py: {exc}")


# ====================================================================== assistant (ai/assistant/)

ASSISTANT_DIR = config.AI_DIR / "assistant"
ASSISTANT_ARMS = ("single_call", "full", "no_repeat", "no_gates", "no_checker")
HEADER_SENTENCE = config.HEADER_COMMENT.lstrip("# ").strip()


def _assistant_headers(rep):
    files = [p for p in sorted(ASSISTANT_DIR.rglob("*")) if p.is_file() and p.suffix in (".py", ".js", ".css", ".sh")
             and not any(part in ("_runtime", "__pycache__") or part.startswith(".")
                         for part in p.relative_to(ASSISTANT_DIR).parts)]
    files += [p for p in (ROOT / "install.sh", ROOT / "run.sh") if p.exists()]
    bad = []
    for p in files:
        head = p.read_text(encoding="utf-8").split("\n")[:3]
        if not any(HEADER_SENTENCE in line for line in head):
            bad.append(_rel(p))
    for b in bad:
        rep.fail("assistant", f"{b}: the AI-generated-code sentence is not in its first lines")
    if not bad:
        rep.ok("assistant", f"{len(files)} assistant code files (.py, .js, .css, .sh, with install.sh and run.sh) "
                            "carry the AI-generated-code sentence")


def _assistant_eval(rep, EV):
    data, errors = EV.load_questions()
    counts, problems = EV.coverage(data)
    for e in errors[:5]:
        rep.fail("assistant", f"eval/questions.json: {e}")
    for pr in problems:
        rep.fail("assistant", f"eval/questions.json coverage: {pr}")
    now, frozen = EV.freeze_state()
    if frozen is None:
        rep.info("assistant", "eval/questions.sha256 is not written yet (python3 -m ai.assistant.evaluate --freeze)")
    elif frozen != now:
        rep.fail("assistant", "eval/questions.json changed after it was frozen in eval/questions.sha256")
    elif not errors and not problems:
        rep.ok("assistant", f"eval/questions.json: {counts['questions']} questions, coverage as required, "
                            f"frozen at {now[:12]}")
    p = INSIGHTS / "assistant_eval.json"
    if not p.exists():
        rep.not_built("assistant", "data/insights/assistant_eval.json (python3 -m ai.assistant.evaluate)")
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    before = len(rep.failures())
    if d.get("fake_model") or d.get("model") != config.MODEL_LABEL:
        rep.fail("assistant", "assistant_eval.json is not a run with the model (fake or no-model run)")
    if d.get("n_questions") != len(data["questions"]):
        rep.fail("assistant", f"assistant_eval.json n_questions {d.get('n_questions')} != {len(data['questions'])}")
    if d.get("questions_sha256") != now:
        rep.fail("assistant", "assistant_eval.json was measured on another questions.json (sha256 differs)")
    arms = d.get("arms") or {}
    extra = [a for a in arms if a not in ASSISTANT_ARMS]
    if extra:
        rep.fail("assistant", f"assistant_eval.json has unknown arms {extra}")
    subsets = d.get("subsets") or {}
    for a, v in arms.items():
        want = data["questions"]
        if a in subsets:  # an ablation arm run on a fixed random part of the set (evaluate.py --subset-arms)
            ids = set(subsets[a].get("ids") or [])
            want = [q for q in data["questions"] if q["id"] in ids]
            if len(want) != len(ids):
                rep.fail("assistant", f"assistant_eval.json arm {a}: its subset names questions not in the set")
        got = {r.get("id") for r in v.get("per_question") or []}
        if len(v.get("per_question") or []) != len(want) or got != {q["id"] for q in want}:
            rep.fail("assistant", f"assistant_eval.json arm {a}: {len(v.get('per_question') or [])} of "
                                  f"{len(want)} questions")
    missing = [a for a in ASSISTANT_ARMS if a not in arms]
    if missing and d.get("complete"):
        rep.fail("assistant", f"assistant_eval.json says complete but lacks arms {missing}")
    if len(rep.failures()) == before:
        if missing:
            rep.info("assistant", f"assistant_eval.json is partial (complete: false): arms {missing} not run")
        rep.ok("assistant", f"assistant_eval.json: arms {sorted(arms)} on {d.get('n_questions')} questions, "
                            "measured on the frozen question set")


def _assistant_recorded(rep, EV):
    p = INSIGHTS / "assistant_recorded.json"
    if not p.exists():
        rep.not_built("assistant", "data/insights/assistant_recorded.json (python3 -m ai.assistant.record)")
        return
    from ai.assistant import check as CK, plan as PL, tools as TL
    from ai import llm
    d = json.loads(p.read_text(encoding="utf-8"))
    schema = EV.design_block("RESPONSE")
    data = TL.Data()
    before = len(rep.failures())
    if d.get("fake_model") or d.get("model") != config.MODEL_LABEL:
        rep.fail("assistant", "assistant_recorded.json is not a recording with the model (fake run)")
    stale, n_turns, n_model = [], 0, 0
    for c in d.get("conversations") or []:
        for i, t in enumerate(c.get("turns") or [], 1):
            n_turns += 1
            where = f"assistant_recorded.json {c.get('id')} turn {i}"
            resp = t.get("response") or {}
            if resp.get("mode") != "recorded":
                rep.fail("assistant", f"{where}: mode is {resp.get('mode')!r}, not 'recorded'")
            errs = llm.validate(resp, schema)
            if errs:
                rep.fail("assistant", f"{where}: not a RESPONSE: {'; '.join(errs[:2])}")
            facts = {f.get("id"): f for f in resp.get("facts") or [] if isinstance(f, dict)}
            answer = resp.get("answer") or {}
            cited_refs = set()
            for s in answer.get("sentences") or []:
                ids = s.get("facts") or []
                if any(x not in facts for x in ids):
                    rep.fail("assistant", f"{where}: sentence {s.get('n')} cites an id that is not a fact of the turn")
                cited_refs |= {facts[x].get("ref") for x in ids if x in facts}
                if (s.get("origin") or answer.get("origin")) == "model":
                    n_model += 1
                    fails = EV.gates(CK.gate_sentence, s.get("text", ""), [facts[x] for x in ids if x in facts],
                                     resp.get("request"), turn_ids=set(facts), cited_ids=ids)
                    for g, r in fails:
                        rep.fail("assistant", f"{where}: sentence {s.get('n')} fails gate {g}: {r}")
            if answer.get("origin") == "model" and \
                    (((resp.get("trace") or {}).get("gate_report") or {}).get("checker_skipped")):
                # a model sentence is shown only after the code gates and the model checker (DESIGN.md 18a)
                rep.fail("assistant", f"{where}: model sentences shown without the model checker")
            req = resp.get("request")
            # every fact of the turn is re-run, not only the cited ones: the page shows all of them under 'Also
            # looked up' and in the facts fold (changed after the grounding audit of 15 Nov)
            if resp.get("kind") == "answer" and isinstance(req, dict) and facts:
                fresh = TL.run(PL.plan(req, data.vocab)[0], data)  # plan() returns (steps, dropped)
                now = defaultdict(set)  # one ref can give several texts (the same tool run for two environments)
                for f in fresh.get("facts") or []:
                    now[f.get("ref")].add(f.get("text"))
                for f in facts.values():
                    if f.get("text") not in now.get(f.get("ref"), set()):
                        stale.append(f"{where} {f.get('ref')}")
    for s_ in stale[:6]:
        rep.fail("assistant", f"recorded answer is stale: run python3 -m ai.assistant.record ({s_})")
    if len(stale) > 6:
        rep.fail("assistant", f"recorded answers: {len(stale)} stale facts in all, "
                              f"{len({x.rsplit(' ', 1)[0] for x in stale})} turns")
    if len(rep.failures()) == before:
        rep.ok("assistant", f"assistant_recorded.json: {n_turns} turns, {n_model} model sentences pass the gates "
                            "against their recorded facts, every fact re-runs to the same text, the model checker ran "
                            "in every model answer")


def check_assistant(rep):
    """The assistant's question set, evaluation and recordings (ai/assistant/DESIGN.md section 15.2)."""
    if not ASSISTANT_DIR.exists():
        rep.not_built("assistant", "ai/assistant/ does not exist")
        return
    _assistant_headers(rep)
    if not (ASSISTANT_DIR / "eval" / "questions.json").exists():
        rep.not_built("assistant", "ai/assistant/eval/questions.json")
        return
    try:
        from ai.assistant import evaluate as EV
    except Exception as exc:  # noqa: BLE001 - reported as a failure
        rep.fail("assistant", f"cannot import ai/assistant/evaluate.py: {type(exc).__name__}: {exc}")
        return
    _assistant_eval(rep, EV)
    try:
        _assistant_recorded(rep, EV)
    except ImportError as exc:
        rep.fail("assistant", f"assistant_recorded.json exists but the assistant cannot be imported: {exc}")


# ====================================================================== report-only lint

def lint_report(rep, live_rank=True):
    hits = []

    def scan(file, key, text):
        if not text:
            return
        for pat in C.lint_text(str(text)):
            hits.append({"file": file, "key": key, "text": str(text), "pattern": pat})
    cfg = json.loads((ROOT / "scoring" / "scoring_config.json").read_text(encoding="utf-8"))
    for k, v in (cfg.get("warnings") or {}).items():
        scan("scoring/scoring_config.json", f"warnings.{k}", v)
    if live_rank:
        from scoring import scorer
        seen = set()
        for _, q in QUERIES:
            r = scorer.rank(q)
            for x in (r.get("results") or []) + (r.get("ranking") or []):
                for fld in ("why", "main_gap"):
                    key = (x.get("config_id"), fld, x.get(fld))
                    if key in seen:
                        continue
                    seen.add(key)
                    scan(f"scoring.scorer.rank({q!r})", f"{x.get('config_id')}.{fld}", x.get(fld))
    for name, idcol in (("investigations.csv", "investigation_id"), ("configurations.csv", "config_id")):
        p = ROOT / "data" / "catalog" / name
        if p.exists():
            for row in _read_csv(p):
                for col in ("objectives", "key_findings"):
                    if col in row:
                        scan(f"data/catalog/{name}", f"{row.get(idcol)}.{col}", row[col])
    rep.lint_hits = hits
    for h in hits:
        rep.add("report", "lint (report-only)", f"{h['file']} {h['key']}: {h['pattern']} :: {h['text'][:140]}")
    if not hits:
        rep.add("report", "lint (report-only)", "no linter hit in files pm does not own")


# ====================================================================== main

def assistant_tests(rep):
    """The assistant's unit tests (fake model, no network), run by build_all through --assistant-tests."""
    env = dict(os.environ, **{llm.NO_CALLS_ENV: "1"})
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "ai/assistant", "-p", "test_*.py"],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    tail = (r.stderr or "").strip().splitlines()
    ran = next((x for x in tail if x.startswith("Ran ")), "no test ran")
    if r.returncode != 0:
        rep.fail("assistant", f"assistant unit tests failed ({ran}): " + " | ".join(tail[-6:]))
    else:
        rep.ok("assistant", f"assistant unit tests (fake model, no network): {ran}, OK")


def run(final=False, live_rank=True, with_assistant_tests=False):
    rep = Report()
    if with_assistant_tests:
        assistant_tests(rep)
    check_headers(rep)
    check_disclosure(rep)
    check_compliance_diff(rep)
    ev = evmod.load() if evmod.EVIDENCE_PATH.exists() else None
    check_evidence(rep, ev)
    rc = recount()
    check_recount(rep, rc)
    if ev is not None:
        check_cards(rep, INSIGHTS / "cards.json", ev, final=final)
        check_scenarios(rep, INSIGHTS / "scenarios.json", ev, recount=rc, live_rank=live_rank)
        check_sheet(rep, INSIGHTS / "cards.json", INSIGHTS / "scenarios.json", ev)
    check_readiness_and_robustness(rep)
    check_assistant(rep)
    lint_report(rep, live_rank=live_rank)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--final", action="store_true", help="fail on any unreviewed model sentence")
    ap.add_argument("--json", action="store_true", help="print the report as JSON")
    ap.add_argument("--assistant-tests", action="store_true",
                    help="also run the assistant's unit tests (fake model, no network)")
    args = ap.parse_args(argv)
    rep = run(final=args.final, with_assistant_tests=args.assistant_tests)
    fails = rep.failures()
    if args.json:
        print(json.dumps({"ok": not fails, "items": rep.items, "lint_hits": rep.lint_hits}, indent=1,
                         ensure_ascii=False))
    else:
        tag = {"ok": "OK  ", "fail": "FAIL", "not_built": "----", "info": "info", "report": "LINT"}
        for x in rep.items:
            print(f"[{tag[x['level']]}] {x['section']}: {x['message']}")
        print(f"\n{'PASS' if not fails else 'FAIL'}: {len(fails)} hard failure(s); "
              f"{sum(x['level'] == 'not_built' for x in rep.items)} file(s) not built yet; "
              f"{len(rep.lint_hits)} report-only lint hit(s)")
        if fails:
            print(f"Rebuild every data/insights/ file in order, with no model call: {REBUILD}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
