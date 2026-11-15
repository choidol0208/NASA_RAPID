# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Lookup tools (ai/assistant/DESIGN.md sections 6 and 7): deterministic code over the team's files.

Each tool returns {"facts": [FACT without id], "panels": [PANEL without id], "notes": [str], "state": {}}.
A fact's text is copied verbatim from a team file or is a template of texts.py filled from a file; its
numbers are listed by code. No tool calls a model or writes a file. run() numbers the facts F1, F2, ...
in plan order and the panels p1, p2, ...

    python3 -m ai.assistant.cli facts counts_per_question '{"env": {"scenario_id": "iss", "label": "ISS cabin"}}'
"""
import csv
import hashlib
import json
import math
import re
import time
from collections import Counter, OrderedDict, defaultdict
from functools import cached_property

from ai import checks, config, lint_patterns as LP
from ai.assistant import request as rq, texts
from scoring import scorer

ROOT = config.ROOT
REPO = "https://github.com/choidol0208/NASA_RAPID"
SITE = "https://choidol0208.github.io/NASA_RAPID"
MAX_WRITER_FACTS = 24

DATA_FILES = (
    "scoring/scoring_config.json", "data/catalog/investigations.csv", "data/catalog/configurations.csv",
    "pipeline/spec/scenarios.json", "pipeline/spec/needs.json", "pipeline/spec/coverage.json",
    "pipeline/spec/variables.json", "pipeline/spec/answers.json", "data/pipeline/tests.csv",
    "data/pipeline/scenario_tests.csv", "data/pipeline/need_tests.csv", "data/pipeline/scenario_needs.csv",
    "data/pipeline/atmosphere_cells.csv", "data/pipeline/need_gap_states.csv", "data/pipeline/retrieval_queue.csv",
    "data/pipeline/test_files.csv", "data/pipeline/raw_file_groups.csv", "data/pipeline/findings.csv",
    "data/pipeline/need_references.csv", "data/insights/model_readiness.json", "data/insights/evidence.json",
    "data/insights/cards.json", "data/pipeline/results_by_need.json",
)


def data_version():
    h = hashlib.sha256()
    paths = [ROOT / p for p in DATA_FILES]
    paths += sorted((ROOT / "data/pipeline/evidence").glob("*.json"))
    paths += sorted((ROOT / "data/pipeline/answers").glob("*.json"))
    paths += sorted((ROOT / "web/dist/data/piles").glob("*.json"))
    for p in paths:
        if p.exists():
            st = p.stat()
            h.update(f"{p.relative_to(ROOT).as_posix()}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    return h.hexdigest()[:12]


def read_commit():
    """The checked-out commit, read from .git without running git; 'main' when it cannot be read."""
    try:
        git = ROOT / ".git"
        head = (git / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            ref = head[5:]
            p = git / ref
            if p.exists():
                return p.read_text().strip()
            packed = git / "packed-refs"
            if packed.exists():
                for line in packed.read_text().splitlines():
                    if line.endswith(" " + ref):
                        return line.split()[0]
            return "main"
        return head if re.fullmatch(r"[0-9a-f]{40}", head) else "main"
    except OSError:
        return "main"


def _g(x):
    return f"{x:g}"


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _rd(x):
    return _g(scorer._r(float(x), 1))


def _joined(parts, last="and"):
    parts = [p for p in parts if p]
    if len(parts) <= 1:
        return "".join(parts)
    return ", ".join(parts[:-1]) + f" {last} " + parts[-1]


def _cap(text, limit=900):
    """Whole sentences of `text` up to `limit` characters (a long team sentence block is cut at a sentence end)."""
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    out = ""
    for s in checks.sentences_of(text) or [text]:
        s = s.strip()
        if len(out) + len(s) + 1 > limit:
            break
        out = (out + " " + s).strip()
    return out or text[:limit].rsplit(" ", 1)[0]


class Data:
    """Loads every file once (cached properties); `version` changes when any listed file changes."""

    def __init__(self):
        self.version = data_version()
        self.commit = read_commit()
        self.vocab = rq.load_vocab(self.version)
        self.cfg = self.vocab["cfg"]
        self._json_cache = {}
        self.files_read = set()

    def link(self, file, line=None):
        if file.startswith("web/dist/"):
            return f"{SITE}/{file[len('web/dist/'):]}"
        url = f"{REPO}/blob/{self.commit}/{file}"
        return url + (f"?plain=1#L{line}" if line else "")

    def json(self, rel):
        self.files_read.add(rel)
        if rel not in self._json_cache:
            self._json_cache[rel] = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        return self._json_cache[rel]

    def _csv(self, rel):
        with open(ROOT / rel, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def csv(self, name):
        self.files_read.add(f"data/pipeline/{name}.csv" if "/" not in name else name)
        return getattr(self, "_c_" + name.replace("/", "_").replace(".", "_"))

    @cached_property
    def _c_tests(self):
        return self._csv("data/pipeline/tests.csv")

    @cached_property
    def tests_by_id(self):
        return {r["test_id"]: (i + 2, r) for i, r in enumerate(self._c_tests)}

    @cached_property
    def _c_scenario_tests(self):
        return self._csv("data/pipeline/scenario_tests.csv")

    @cached_property
    def _c_need_tests(self):
        return self._csv("data/pipeline/need_tests.csv")

    @cached_property
    def _c_scenario_needs(self):
        return self._csv("data/pipeline/scenario_needs.csv")

    @cached_property
    def _c_atmosphere_cells(self):
        return self._csv("data/pipeline/atmosphere_cells.csv")

    @cached_property
    def _c_need_gap_states(self):
        return self._csv("data/pipeline/need_gap_states.csv")

    @cached_property
    def _c_retrieval_queue(self):
        return self._csv("data/pipeline/retrieval_queue.csv")

    @cached_property
    def _c_test_files(self):
        return self._csv("data/pipeline/test_files.csv")

    @cached_property
    def _c_raw_file_groups(self):
        return self._csv("data/pipeline/raw_file_groups.csv")

    @cached_property
    def _c_findings(self):
        return self._csv("data/pipeline/findings.csv")

    @cached_property
    def _c_need_references(self):
        return self._csv("data/pipeline/need_references.csv")

    @cached_property
    def catalog(self):
        self.files_read.update({"data/catalog/investigations.csv", "data/catalog/configurations.csv"})
        return scorer.load_catalog()

    @cached_property
    def config_lines(self):
        with open(ROOT / "data/catalog/configurations.csv", newline="", encoding="utf-8") as f:
            return {r["config_id"]: i + 2 for i, r in enumerate(csv.DictReader(f))}

    @cached_property
    def inv_lines(self):
        with open(ROOT / "data/catalog/investigations.csv", newline="", encoding="utf-8") as f:
            return {r["psi_accession"]: i + 2 for i, r in enumerate(csv.DictReader(f))}

    @cached_property
    def evidence(self):
        return self.json("data/insights/evidence.json")["records"]

    @cached_property
    def needs(self):
        return {n["id"]: n for n in self.json("pipeline/spec/needs.json")["needs"]}

    @cached_property
    def variables(self):
        return self.json("pipeline/spec/variables.json")

    @cached_property
    def piles(self):
        """{scenario: piles doc}: web/dist/data/piles/<sid>.json when built, else web.raw_piles.build()."""
        out, notes = {}, []
        for sid in ("iss", "lunar_habitat"):
            p = ROOT / "web/dist/data/piles" / f"{sid}.json"
            if p.exists():
                out[sid] = (json.loads(p.read_text(encoding="utf-8")), f"web/dist/data/piles/{sid}.json")
        if len(out) < 2:
            try:
                from web import raw_piles
                built = raw_piles.build(str(ROOT))
                for sid, doc in built.items():
                    out.setdefault(sid, (doc, "web/raw_piles.py"))
            except Exception as e:  # noqa: BLE001 - fall back to gap states and say so
                notes.append(f"raw_piles failed: {type(e).__name__}")
        self.pile_notes = notes
        return out

    def name(self, acc):
        r = self.vocab["investigations"].get(acc)
        return r["short"] if r else acc

    def psi_url(self, acc):
        r = self.vocab["investigations"].get(acc)
        return r["psi_url"] if r else None

    @cached_property
    def search_index(self):
        units, df = [], Counter()
        for acc, rec in self.evidence.items():
            title = _stems(rec.get("title") or "")
            for u in rec["units"]:
                if not u.get("quotable"):
                    continue
                st = _stems(u["text"])
                units.append({"acc": acc, "unit": u, "stems": st, "title": title})
                df.update(st)
        n = len(units)
        idf = {s: math.log(n / c) for s, c in df.items()}
        return {"units": units, "idf": idf, "n": n, "k": len(self.evidence)}

    @cached_property
    def glossary(self):
        return _build_glossary(self)


def _stems(text):
    return {checks._stem(w) for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if len(w) >= 3 and w not in checks._STOP}


# ---------------------------------------------------------------- fact helpers
def fact(tool, kind, text, *, ref, file, line=None, key=None, context=None, link=None, quote=False, field=None,
         invs=(), lead=False, limit=False, source_keys=(), what="a value in the text"):
    nums, seen = [], set()
    for part in (context or "", text):
        for n in checks.extract_numbers(part):
            k = (float(n["value"]), n["unit"])
            if k not in seen:
                seen.add(k)
                nums.append({"value": float(n["value"]), "unit": n["unit"], "what": what})
        for w in checks.number_words(part):
            k = (float(LP.NUMBER_WORDS[w]), None)
            if k not in seen:
                seen.add(k)
                nums.append({"value": float(LP.NUMBER_WORDS[w]), "unit": None, "what": "a number word in the text"})
    return {"ref": ref[:200], "tool": tool, "kind": kind, "context": (context or None) and context[:160],
            "text": _cap(text), "numbers": nums, "source": {"file": file, "line": line, "key": key},
            "source_keys": list(source_keys), "link": link, "quote": bool(quote), "field": field,
            "investigation_ids": list(invs), "lead": bool(lead), "limit": bool(limit)}


def panel(ptype, title, columns, rows, *, note=None, download=None, section=None, fact_refs=()):
    return {"type": ptype, "title": title[:120], "note": note, "columns": columns, "rows": rows[:500],
            "download": download, "dashboard_section": section, "fact_refs": list(fact_refs)}


def col(key, label, kind="text"):
    return {"key": key, "label": label, "kind": kind}


def missing(name):
    return {"facts": [], "panels": [], "notes": [f"missing argument {name}"], "state": {}}


def _out(facts, panels=(), notes=(), state=None):
    return {"facts": facts, "panels": list(panels), "notes": list(notes), "state": state or {}}


def _env_ok(env):
    return isinstance(env, dict) and (env.get("scenario_id") or env.get("cell"))


def _label(env):
    return env.get("label") or env.get("scenario_id") or (env.get("cell") or {}).get("id") or "this environment"


def _qids(data, qs):
    qs = [q for q in (qs or []) if q in data.needs]
    return qs or list(data.needs)


# ---------------------------------------------------------------- 7.1 rank_investigations
def rank_investigations(args, data):
    q = args.get("q")
    if not q:
        return missing("q")
    T = "rank_investigations"
    out = scorer.rank(q, config=data.cfg, catalog=data.catalog)
    data.files_read.add("scoring/scoring_config.json")
    F = []
    src = "data/catalog/configurations.csv"
    if out["status"] != "ok":
        for w in out["warnings"]:
            F.append(fact(T, "limit", w["message"], ref=f"scorer#{w['code']}", file="scoring/scoring_config.json",
                          key=f"warnings.{w['code']}", link=data.link("scoring/scoring_config.json"), limit=True))
        return _out(F)
    res = out["results"]
    accs = [r["psi_accession"] for r in res]
    lst = ", ".join(f"{data.name(a)} ({a})" for a in accs)
    F.append(fact(T, "ranking", texts.T["rank_list"].format(list=lst), ref=f"scorer.rank#{q}", file=src,
                  key=f"rank({q!r})", link=data.link("scoring/scorer.py"), invs=accs, lead=True))
    for r in res[:3]:
        why = "; ".join(r["why"]) if isinstance(r["why"], list) else str(r["why"] or "")
        line = data.config_lines.get(r["config_id"])
        F.append(fact(T, "ranking", texts.T["rank_result"].format(name=data.name(r["psi_accession"]),
                      acc=r["psi_accession"], config=r["config_label"], why=why.rstrip(".")),
                      ref=f"configurations.csv#{r['config_id']}", file=src, line=line, key=r["config_id"],
                      link=data.link(src, line), invs=[r["psi_accession"]]))
    for r in res[:3]:
        if r.get("main_gap"):
            line = data.config_lines.get(r["config_id"])
            F.append(fact(T, "ranking", texts.T["rank_gap"].format(name=data.name(r["psi_accession"]),
                          acc=r["psi_accession"], gap=str(r["main_gap"]).rstrip(".")),
                          ref=f"configurations.csv#{r['config_id']}/main_gap", file=src, line=line,
                          key=r["config_id"], link=data.link(src, line), invs=[r["psi_accession"]]))
    for w in out["warnings"]:
        F.append(fact(T, "limit", w["message"], ref=f"scorer#{w['code']}", file="scoring/scoring_config.json",
                      key=f"warnings.{w['code']}", link=data.link("scoring/scoring_config.json"), limit=True))
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#rank_limit", file="ai/assistant/texts.py",
                  key="LIMITS.rank_investigations", link=data.link("ai/assistant/texts.py"), limit=True))
    rows = [{"investigation": data.name(r["psi_accession"]), "accession": r["psi_accession"],
             "configuration": r["config_label"], "score": r["score"],
             "why": "; ".join(r["why"]) if isinstance(r["why"], list) else r["why"], "main_gap": r.get("main_gap"),
             "record": {"text": r["psi_accession"], "href": r["psi_url"]}} for r in res]
    P = [panel("ranking", "Closest NASA investigations (team's ranking)",
               [col("investigation", "investigation"), col("accession", "accession"),
                col("configuration", "configuration"), col("score", "team score (0 to 100)", "number"),
                col("why", "why"), col("main_gap", "main gap"), col("record", "record", "link")],
               rows, note=texts.LIMITS[T], section="#top")]
    return _out(F, P, state={"last_list": accs})


# ---------------------------------------------------------------- 7.2 counts_per_question
WANT_STATEMENT = re.compile(r"^(status\.|tiers\.counts$|matched\.|gravity\.compared$|gap\.|need\.reading$)")


def _package(env):
    if env.get("scenario_id"):
        return f"data/pipeline/evidence/scenario_{env['scenario_id']}.json"
    return f"data/pipeline/evidence/{env['cell']['id']}.json"


def counts_per_question(args, data):
    env = args.get("env")
    if not _env_ok(env):
        return missing("env")
    T = "counts_per_question"
    rel = _package(env)
    if not (ROOT / rel).exists():
        return _out([], notes=[f"no evidence package {rel}"])
    pkg = data.json(rel)
    label = _label(env)
    qs = _qids(data, args.get("questions"))
    F, leads = [], 0
    link = data.link(rel)
    if env.get("cell") and not env.get("scenario_id"):
        F.append(fact(T, "limit", texts.T["counts_cell"].format(label=pkg["environment"]["label"]),
                      ref=f"{rel}#environment.label", file=rel, key="environment.label", link=link, limit=True))
    if env.get("scenario_id") == "mars_habitat":
        sc = data.vocab["presets"]["mars_habitat"]
        if sc.get("note"):
            F.append(fact(T, "limit", sc["note"], ref="scenarios.json#mars_habitat/note",
                          file="pipeline/spec/scenarios.json", key="scenarios[mars_habitat].note",
                          link=data.link("pipeline/spec/scenarios.json"), limit=True))
    blocks = {b["need_id"]: b for b in pkg["needs"]}
    for q in qs:
        b = blocks.get(q)
        if not b:
            continue
        ctx = f"{label}; {b['need']} ({q})"
        for s in b["statements"]:
            sid = s["id"]
            if not WANT_STATEMENT.match(sid):
                continue
            is_lead = sid.startswith("status.") and leads < 2
            leads += is_lead
            kind = "limit" if sid == "need.reading" else "statement" if not sid.startswith("tiers") else "count"
            F.append(fact(T, kind, s["text"], ref=f"evidence/{rel.rsplit('/', 1)[1]}#{q}/{sid}", file=rel,
                          key=f"needs.{q}.statements[{sid}]", context=ctx, link=link, invs=_accs_in(s["text"]),
                          lead=is_lead, limit=(sid == "need.reading")))
        if env.get("scenario_id"):
            arel = f"data/pipeline/answers/{env['scenario_id']}__{q}.json"
            if (ROOT / arel).exists():
                a = data.json(arel)
                tl = (a.get("top_line") or {}).get("text")
                if tl:
                    F.append(fact(T, "statement", tl, ref=f"answers/{env['scenario_id']}__{q}.json#top_line",
                                  file=arel, key="top_line.text", context=ctx, link=data.link(arel),
                                  invs=_accs_in(tl)))
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#counts_limit", file="ai/assistant/texts.py",
                  key="LIMITS.counts_per_question", link=data.link("ai/assistant/texts.py"), limit=True))
    if env.get("scenario_id"):
        rows_src = [r for r in data.csv("scenario_needs") if r["scenario_id"] == env["scenario_id"]]
    else:
        rows_src = [r for r in data.csv("atmosphere_cells") if r["scenario_id"] == env["cell"]["id"]]
    rows = [{"question": r["need_id"], "name": r["need"], "counted": int(r["usable_tests"]),
             "both_inside": int(r["tests_atmosphere"]), "oxygen_only": int(r["tests_oxygen_only"]),
             "pressure_only": int(r["tests_pressure_only"]), "elsewhere": int(r["tests_other"]), "status": r["status"]}
            for r in rows_src if r["need_id"] in qs]
    P = [panel("counts", f"Recorded tests per fire-safety question: {label}",
               [col("question", "question"), col("name", "name"), col("counted", "counted", "number"),
                col("both_inside", "both inside", "number"), col("oxygen_only", "oxygen only", "number"),
                col("pressure_only", "pressure only", "number"), col("elsewhere", "elsewhere", "number"),
                col("status", "status")], rows, note=texts.LIMITS[T], section="#needs")]
    return _out(F, P)


def _accs_in(text):
    return list(dict.fromkeys(re.findall(r"\bPSI-\d+\b", text or "")))


# ---------------------------------------------------------------- 7.3 tested_range
def _range_stats(data, phase):
    rows = [r for r in data.csv("tests") if r["fuel_phase"] == phase]
    o2 = [_num(r["o2_pct"]) for r in rows if r["o2_basis"] == "ambient" and _num(r["o2_pct"]) is not None]
    stream = [r for r in rows if r["o2_basis"] == "oxidizer_stream"]
    pr = [_num(r["pressure_kpa"]) for r in rows if _num(r["pressure_kpa"]) is not None]
    return {"n": len(rows), "o2": o2, "stream": stream, "p": pr}


def _position(v, vals):
    if not vals:
        return texts.POSITION["none"]
    lo, hi = scorer._r(min(vals), 1), scorer._r(max(vals), 1)
    if v < lo:
        return texts.POSITION["below"]
    if v > hi:
        return texts.POSITION["above"]
    return texts.POSITION["within"]


def _bar_text(nb):
    """'... solid fuels: cannot be placed from the tables 237 | outside by a recorded value 139.' is the page's bar
    label; said as a sentence, each count comes before its words (changed after the clean-clone check of 15 Nov)."""
    bar, segs = nb.get("bar") or "", nb.get("segments") or []
    if not segs or ":" not in bar or not all(isinstance(x.get("n"), int) and x.get("label") for x in segs):
        return bar
    return bar.split(":", 1)[0] + ": " + "; ".join(f"{x['n']} {x['label']}" for x in segs) + "."


def tested_range(args, data):
    env = args.get("env") or {}
    T = "tested_range"
    phase = args.get("phase")
    phases = [phase] if phase in ("solid", "liquid", "gas") else ["solid", "liquid", "gas"]
    src = "data/pipeline/tests.csv"
    link = data.link(src)
    o2v, pv = env.get("o2_pct"), env.get("pressure_kpa")
    F, rows, leads = [], [], 0
    for ph in phases:
        st = _range_stats(data, ph)
        pw = texts.PHASE_WORDS[ph]
        pre = args.get("preset_values") or []
        your = texts.T["range_o2_preset" if "o2" in pre else "range_o2_your"].format(
            value=_g(o2v), position=_position(o2v, st["o2"])) if o2v is not None else ""
        if st["o2"]:
            t = texts.T["range_o2"].format(phase=pw, k=len(st["o2"]), n=st["n"], lo=_rd(min(st["o2"])),
                                           hi=_rd(max(st["o2"])), your=your)
        else:
            t = texts.T["range_o2_none"].format(phase=pw, k=0, n=st["n"], your=your)
        F.append(fact(T, "range", t, ref=f"tests.csv#o2_pct/{ph}", file=src, key=f"o2_pct, fuel_phase={ph}, o2_basis=ambient",
                      link=link, lead=leads < 2))
        leads += 1
        yp = texts.T["range_p_preset" if "p" in pre else "range_p_your"].format(
            value=_g(pv), position=_position(pv, st["p"])) if pv is not None else ""
        span = texts.T["range_p_span"].format(lo=_rd(min(st["p"])), hi=_rd(max(st["p"]))) if st["p"] else ""
        F.append(fact(T, "range", texts.T["range_p"].format(phase=pw, k=len(st["p"]), n=st["n"], span=span, your=yp),
                      ref=f"tests.csv#pressure_kpa/{ph}", file=src, key=f"pressure_kpa, fuel_phase={ph}", link=link,
                      lead=leads < 2))
        leads += 1
        if st["stream"]:
            srcs = sorted({f"pipeline/spec/sources.json#{r['source_id']}" for r in st["stream"]})
            F.append(fact(T, "range", texts.T["range_stream"].format(m=len(st["stream"]),
                          phase_lower=texts.PHASE_OF[ph]), ref=f"tests.csv#o2_basis=oxidizer_stream/{ph}", file=src,
                          key=f"o2_basis=oxidizer_stream, fuel_phase={ph}", link=link, source_keys=srcs))
        rows.append({"fuel_phase": ph, "tests": st["n"], "oxygen_recorded": len(st["o2"]),
                     "oxygen_span": f"{_rd(min(st['o2']))} to {_rd(max(st['o2']))}" if st["o2"] else None,
                     "your_oxygen": o2v, "pressure_recorded": len(st["p"]),
                     "pressure_span": f"{_rd(min(st['p']))} to {_rd(max(st['p']))}" if st["p"] else None,
                     "your_pressure": pv})
    if env.get("gravity") in ("lunar", "martian", "earth"):
        mr = data.json("data/insights/model_readiness.json")
        s = next((x for x in mr["not_covered"] if x.startswith("No table has a partial-gravity test")), None)
        if s:
            F.append(fact(T, "limit", s, ref="model_readiness.json#not_covered/gravity",
                          file="data/insights/model_readiness.json", key="not_covered[gravity]",
                          link=data.link("data/insights/model_readiness.json"), limit=True))
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#range_limit", file="ai/assistant/texts.py",
                  key="LIMITS.tested_range", link=data.link("ai/assistant/texts.py"), limit=True))
    P = [panel("range", "Your values against the recorded tests",
               [col("fuel_phase", "fuel phase"), col("tests", "tests", "number"),
                col("oxygen_recorded", "oxygen recorded", "number"), col("oxygen_span", "oxygen span (%)"),
                col("your_oxygen", "your oxygen", "number"), col("pressure_recorded", "pressure recorded", "number"),
                col("pressure_span", "pressure span (kPa)"), col("your_pressure", "your pressure", "number")],
               rows, note=texts.LIMITS[T], section="#stops")]
    return _out(F, P)


# ---------------------------------------------------------------- 7.4 where_the_data_are
def _var_words(v):
    try:
        from web import raw_piles
        return raw_piles.VAR_WORDS.get(v, v.replace("_", " "))
    except Exception:  # noqa: BLE001
        return v.replace("_", " ")


def _size(b):
    from web import raw_piles
    return raw_piles.size(b)


def _gap_facts(data, T, scenario, qs, *, per_need=3, label=None):
    F, rows_by_need = [], defaultdict(lambda: {"in": [], "archive": [], "none": []})
    rq_rows = data.csv("retrieval_queue")
    first_by_var = {}
    for r in sorted(rq_rows, key=lambda r: int(r["rank"])):
        first_by_var.setdefault(r["variable"], r)
    src = "data/pipeline/need_gap_states.csv"
    gs = data.csv("need_gap_states")
    for q in qs:
        n_ = 0
        need = data.needs[q]
        for i, r in enumerate(gs):
            if r["scenario_id"] != scenario or r["need_id"] != q or r["role"] not in ("required", "outcome"):
                continue
            k = int(r["counted_tests_in_state"] or 0)
            words = _var_words(r["variable"])
            bucket = "in" if r["state"] == "in_table" else ("archive" if r["state"] in (
                "column_in_sampled_raw_file", "documented_only") else "none")
            if int(r["in_scope_tests_in_state"] or 0) > 0:
                rows_by_need[q][bucket].append(f"{words} ({texts.STATE_WORDS.get(r['state'], r['state'])})")
            if r["state"] == "in_table" or k == 0 or n_ >= per_need:
                continue
            n_ += 1
            F.append(fact(T, "statement", texts.T["gap_state"].format(need=need["name"], nid=q, var=words, k=k,
                          n=int(r["counted_tests"]), state=texts.STATE_WORDS.get(r["state"], r["state"])),
                          ref=f"need_gap_states.csv#{scenario}/{q}/{r['variable']}/{r['state']}", file=src, line=i + 2,
                          context=(f"{label}; {need['name']} ({q})" if label else None), link=data.link(src, i + 2)))
            fr = first_by_var.get(r["variable"])
            if fr:
                line = rq_rows.index(fr) + 2
                F.append(fact(T, "statement", texts.T["reading_order"].format(
                    var=words, pattern=fr["name_pattern"], inv=f"{data.name(fr['investigation_id'])} ({fr['investigation_id']})",
                    files=int(fr["files"]), size=_size(fr["bytes"])),
                    ref=f"retrieval_queue.csv#{fr['rank']}", file="data/pipeline/retrieval_queue.csv", line=line,
                    link=data.link("data/pipeline/retrieval_queue.csv", line), invs=[fr["investigation_id"]]))
    return F, rows_by_need


def where_the_data_are(args, data):
    env = args.get("env")
    if not _env_ok(env):
        return missing("env")
    T = "where_the_data_are"
    qs = _qids(data, args.get("questions"))
    sid = env.get("scenario_id")
    label = _label(env)
    F, rows, notes = [], [], []
    piles = data.piles if sid in ("iss", "lunar_habitat") else {}
    notes += getattr(data, "pile_notes", [])
    if sid in piles:
        doc, rel = piles[sid]
        link = data.link(rel) if rel.startswith("web/dist/") else data.link("web/raw_piles.py")
        data.files_read.add(rel)
        for i, h in enumerate(doc["header"]):
            F.append(fact(T, "pile", h, ref=f"piles/{sid}.json#header/{i}", file=rel, key=f"header[{i}]", link=link,
                          lead=(i == 0)))
        leads = 1
        for nb in doc["needs"]:
            if nb["id"] not in qs:
                continue
            ctx = f"{label}; {nb['name']} ({nb['id']})"
            F.append(fact(T, "pile", _bar_text(nb), ref=f"piles/{sid}.json#{nb['id']}/bar", file=rel,
                          key=f"needs[{nb['id']}].bar", context=ctx, link=link, lead=leads < 2))
            leads += 1
            for k in ("pile1", "pile2", "shelf", "pile3"):
                for j, line in enumerate(nb.get(k) or []):
                    F.append(fact(T, "pile", line, ref=f"piles/{sid}.json#{nb['id']}/{k}/{j}", file=rel,
                                  key=f"needs[{nb['id']}].{k}[{j}]", context=ctx, link=link, invs=_accs_in(line)))
            rows.append({"question": nb["id"], "bar": _bar_text(nb), "tables": (nb.get("pile1") or []) + (nb.get("shelf") or []),
                         "archive": nb.get("pile2") or [], "no_record": nb.get("pile3") or []})
        for i, s in enumerate(doc["small_print"]):
            F.append(fact(T, "limit", s, ref=f"piles/{sid}.json#small_print/{i}", file=rel, key=f"small_print[{i}]",
                          link=link, limit=True))
        note = " ".join(doc["small_print"])
        cols = [col("question", "question"), col("bar", "bar"), col("tables", "in NASA's tables", "list"),
                col("archive", "in the archive", "list"), col("no_record", doc.get("pile3_label") or "no record in PSI", "list")]
    else:
        scen = sid or "iss"
        F, by = _gap_facts(data, T, scen, qs, label=label)
        for q in qs:
            rows.append({"question": q, "bar": None, "tables": by[q]["in"], "archive": by[q]["archive"],
                         "no_record": by[q]["none"]})
        F.append(fact(T, "limit", texts.LIMITS["where_gap_states"], ref="texts#where_limit", file="ai/assistant/texts.py",
                      key="LIMITS.where_gap_states", link=data.link("ai/assistant/texts.py"), limit=True))
        for f in F[:2]:
            f["lead"] = True
        note = texts.LIMITS["where_gap_states"]
        cols = [col("question", "question"), col("bar", "bar"), col("tables", "in NASA's tables", "list"),
                col("archive", "in the archive", "list"), col("no_record", "not found in the files opened", "list")]
    P = [panel("piles", f"Where the data are: {label}", cols, rows, note=note, section="#piles")]
    return _out(F, P, notes)


# ---------------------------------------------------------------- 7.5 tests_table
def _cell_tests(data, cell):
    ob = next(b for b in data.vocab["o2_bins"] if b["id"] == cell["o2_bin"])
    pb = next(b for b in data.vocab["p_bins"] if b["id"] == cell["pressure_bin"])
    out = []
    for r in data.csv("tests"):
        o2, p = _num(r["o2_pct"]), _num(r["pressure_kpa"])
        if r["o2_basis"] == "ambient" and o2 is not None and p is not None and rq._in_range(o2, ob) and rq._in_range(p, pb):
            out.append((r["test_id"], "cell"))
    return out


def tests_table(args, data):
    env = args.get("env")
    if not _env_ok(env):
        return missing("env")
    T = "tests_table"
    q = args.get("question") if args.get("question") in data.needs else None
    limit = int(args.get("limit") or 500)
    if env.get("scenario_id"):
        pairs = [(r["test_id"], r["tier"]) for r in data.csv("scenario_tests")
                 if r["scenario_id"] == env["scenario_id"] and r["tier"] in ("atmosphere", "oxygen_only", "pressure_only")]
    else:
        pairs = _cell_tests(data, env["cell"])
    links = {}
    if q:
        links = {r["test_id"]: r["objective_link"] for r in data.csv("need_tests") if r["need_id"] == q}
        pairs = [p for p in pairs if p[0] in links]
    label = _label(env)
    need = data.needs.get(q) if q else None
    qwords = texts.T["tests_qwords"].format(need=need["name"], nid=q) if need else ""
    tiers = Counter(t for _, t in pairs)
    src = "data/pipeline/tests.csv"
    F = []
    if env.get("scenario_id"):
        parts = texts.T["tests_tiers_parts"].format(a=tiers.get("atmosphere", 0), o=tiers.get("oxygen_only", 0),
                                                    p=tiers.get("pressure_only", 0))
        F.append(fact(T, "count", texts.T["tests_tiers"].format(n=len(pairs), qwords=qwords, tiers=parts),
                      ref=f"scenario_tests.csv#{env['scenario_id']}/{q or 'all'}", file="data/pipeline/scenario_tests.csv",
                      key=f"scenario_id={env['scenario_id']}", context=label,
                      link=data.link("data/pipeline/scenario_tests.csv"), lead=True))
    else:
        F.append(fact(T, "count", texts.T["tests_cell"].format(n=len(pairs), qwords=qwords),
                      ref=f"tests.csv#{env['cell']['id']}/{q or 'all'}", file=src, key=env["cell"]["id"],
                      context=label, link=data.link(src), lead=True))
    by_inv = Counter()
    for tid, _ in pairs:
        line, r = data.tests_by_id[tid]
        by_inv[(r["investigation_id"], r["fuel_phase"])] += 1
    for (acc, ph), k in sorted(by_inv.items(), key=lambda x: (-x[1], x[0]))[:6]:
        F.append(fact(T, "count", texts.T["tests_inv"].format(k=k, phase=texts.PHASE_OF.get(ph, ph + " tests"),
                      name=data.name(acc), acc=acc), ref=f"tests.csv#{acc}/{ph}/{q or 'all'}", file=src,
                      key=f"investigation_id={acc}, fuel_phase={ph}", context=label, link=data.link(src), invs=[acc]))
    if env.get("cell") and not env.get("scenario_id"):
        F.append(fact(T, "limit", texts.T["tests_cell_limit"], ref="texts#tests_cell_limit", file="ai/assistant/texts.py",
                      key="T.tests_cell_limit", link=data.link("ai/assistant/texts.py"), limit=True))
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#tests_limit", file="ai/assistant/texts.py",
                  key="LIMITS.tests_table", link=data.link("ai/assistant/texts.py"), limit=True))
    outs = need["outcomes_any"] if need else []
    rows = []
    for tid, tier in pairs[:limit]:
        line, r = data.tests_by_id[tid]
        row = {"test_id": {"text": tid, "href": data.link(src, line)}, "investigation": r["investigation_id"],
               "tier": texts.TIER_WORDS.get(tier, tier), "fuel_phase": r["fuel_phase"], "fuel": r["fuel_material"],
               "o2_pct": _num(r["o2_pct"]), "o2_basis": r["o2_basis"], "pressure_kpa": _num(r["pressure_kpa"]),
               "flow_cms": _num(r["flow_cms"]), "gravity": r["gravity_level"]}
        for o in outs:
            row[o] = r.get(o) or None
        row["objective_link"] = links.get(tid) if q else None
        row["source_file"] = r["source_file"]
        row["source_row"] = r["source_row"]
        rows.append(row)
    cols = [col("test_id", "test id", "link"), col("investigation", "investigation"), col("tier", "tier"),
            col("fuel_phase", "fuel phase"), col("fuel", "fuel"), col("o2_pct", "oxygen (%)", "number"),
            col("o2_basis", "oxygen basis"), col("pressure_kpa", "pressure (kPa)", "number"),
            col("flow_cms", "flow (cm/s)", "number"), col("gravity", "gravity")]
    cols += [col(o, _var_words(o)) for o in outs]
    cols += [col("objective_link", "objective link"), col("source_file", "source file"), col("source_row", "source row")]
    note = texts.LIMITS[T]
    if len(pairs) > limit:
        note += " " + texts.T["tests_first"].format(n=limit, total=len(pairs), file="data/pipeline/tests.csv")
    envkey = env.get("scenario_id") or env["cell"]["id"]
    P = [panel("table", f"Recorded tests: {label}" + (f", {need['name']} ({q})" if need else ""), cols, rows, note=note,
               download={"filename": f"tests_{envkey}_{q or 'all'}.csv", "total_rows": len(pairs)}, section="#tests")]
    return _out(F, P, state={"last_tests": [t for t, _ in pairs[:10]]})


# ---------------------------------------------------------------- 7.6 modelling_data
READINESS_Q = {"test_end": ["S1"], "extinction_to_initial_diameter_ratio": ["S1"], "flow_event": ["P1", "S1"],
               "hot_ignition": ["P2"], "spread_rate_mm_s": ["P3"], "burn_length_cm": ["P3"]}


def _var_unit(data, v):
    var = data.variables.get("variables", {}).get(v) or data.variables.get("derived", {}).get(v) or {}
    unit = var.get("unit") if isinstance(var, dict) else None
    words = _var_words(v)
    return f"{words} ({unit})" if unit and unit not in ("", "id in materials.json") and "|" not in unit else words


def modelling_data(args, data):
    T = "modelling_data"
    qs = _qids(data, args.get("questions"))
    invs = [a for a in (args.get("investigations") or []) if a in data.vocab["investigations"]]
    rel = "data/insights/model_readiness.json"
    mr = data.json(rel)
    link = data.link(rel)
    # the fixed line 'None is a cabin-material flammability model.' does not stand alone as a lead sentence (a
    # judge read it as a leaked Python None): it is said with what 'none' counts (changed after the clean-clone
    # check of 15 Nov)
    fl = mr["fixed_line"]
    if fl.startswith("None is "):
        fl = f"None of the team's {len(mr['rows'])} statistical diagnostics on NASA PSI tables is " + fl[len("None is "):]
    F = [fact(T, "readiness", fl, ref="model_readiness.json#fixed_line", file=rel, key="fixed_line",
              link=link, lead=True),
         fact(T, "limit", mr["labels_and_limits"], ref="model_readiness.json#labels_and_limits", file=rel,
              key="labels_and_limits", link=link, limit=True)]
    prow = []
    for i, r in enumerate(mr["rows"]):
        rq_ = READINESS_Q.get(r["column"], [])
        if not set(rq_) & set(qs) or (invs and r["investigation_id"] not in invs):
            continue
        F.append(fact(T, "readiness", texts.T["ready_row"].format(label=r["label"], inv=r["investigation_id"],
                      n=r["n"], verdict=r["verdict"]), ref=f"model_readiness.json#rows/{r['id']}", file=rel,
                      key=f"rows[{i}]", link=link, invs=[r["investigation_id"]]))
        prow.append({"label": r["label"], "investigation": r["investigation_id"], "tests": r["n"], "groups": r["groups"],
                     "verdict": r["verdict"]})
    counted = Counter(r["need_id"] for r in data.csv("need_tests") if r["objective_link"] == "stated")
    for q in qs:
        need = data.needs[q]
        if not any(set(READINESS_Q.get(r["column"], [])) & {q} for r in mr["rows"]):
            F.append(fact(T, "readiness", texts.T["ready_none"].format(need=need["name"], nid=q),
                          ref=f"model_readiness.json#none/{q}", file=rel, key="rows", link=link))
        F.append(fact(T, "statement", texts.T["ready_need"].format(
            need=need["name"], nid=q, counted=counted.get(q, 0),
            required=_joined([_var_unit(data, v) for v in need["conditions_required"]]),
            outcomes=_joined([_var_unit(data, v) for v in need["outcomes_any"]], "or")),
            ref=f"needs.json#{q}/variables", file="pipeline/spec/needs.json", key=f"needs[{q}]",
            link=data.link("pipeline/spec/needs.json")))
    gf, _ = _gap_facts(data, T, "iss", qs, per_need=2)
    F += gf
    P = [panel("readiness", "Can these NASA tables support an outcome model? (team's diagnostic)",
               [col("label", "label"), col("investigation", "investigation"), col("tests", "tests", "number"),
                col("groups", "groups", "number"), col("verdict", "verdict")], prow, note=mr["labels_and_limits"],
               section="#ai-use")]
    q0 = qs[0]
    need = data.needs[q0]
    ids = [r["test_id"] for r in data.csv("need_tests") if r["need_id"] == q0 and r["objective_link"] == "stated"]
    vars_ = list(dict.fromkeys(need["conditions_required"] + need["outcomes_any"]))
    rows = []
    for tid in ids[:500]:
        line, r = data.tests_by_id[tid]
        row = {"test_id": {"text": tid, "href": data.link("data/pipeline/tests.csv", line)},
               "investigation": r["investigation_id"]}
        for v in vars_:
            row[v] = r.get(v) or None
        rows.append(row)
    P.append(panel("table", f"Counted tests for {need['name']} ({q0}) with its variables",
                   [col("test_id", "test id", "link"), col("investigation", "investigation")]
                   + [col(v, _var_unit(data, v)) for v in vars_], rows, note=mr["labels_and_limits"],
                   download={"filename": f"modelling_{q0}.csv", "total_rows": len(ids)}, section="#ai-use"))
    return _out(F, P)


# ---------------------------------------------------------------- 7.9 search_records
def _nasa_fact(data, T, acc, u, score=None):
    text = texts.T["nasa_sentence"].format(name=data.name(acc), acc=acc,
                                           field=texts.FIELD_LABELS.get(u["field"], u["field"]), sentence=u["text"])
    return fact(T, "nasa_sentence", text, ref=f"evidence.json#{acc}/{u['id']}", file="data/insights/evidence.json",
                key=f"records.{acc}.units[{u['id']}]", link=data.psi_url(acc), quote=True, field=u["field"],
                invs=[acc], what="a value in the record's sentence")


def _quote_row(data, acc, u):
    rec = data.evidence[acc]
    doi = rec.get("dataset_doi")
    return {"investigation": f"{data.name(acc)} ({acc})", "field": texts.FIELD_LABELS.get(u["field"], u["field"]),
            "sentence": u["text"], "record": {"text": acc, "href": data.psi_url(acc)},
            "doi": {"text": doi, "href": f"https://doi.org/{doi}"} if doi else None}


QUOTE_COLS = [col("investigation", "investigation"), col("field", "field"), col("sentence", "sentence"),
              col("record", "record", "link"), col("doi", "dataset DOI", "link")]


def _search(data, keywords, invs=(), fields=(), limit=5):
    idx = data.search_index
    qst = set()
    for k in keywords or []:
        qst |= _stems(k)
    hits = []
    order = {a: i for i, a in enumerate(sorted(data.evidence, key=lambda a: int(a.split("-")[1])))}
    for j, x in enumerate(idx["units"]):
        if invs and x["acc"] not in invs:
            continue
        if fields and x["unit"]["field"] not in fields:
            continue
        s = sum(idx["idf"].get(t, 0) for t in qst if t in x["stems"]) + sum(0.5 for t in qst if t in x["title"])
        if s > 0:
            hits.append((-s, order[x["acc"]], j, x))
    hits.sort(key=lambda h: h[:3])
    return [h[3] for h in hits[:limit]]


def search_records(args, data):
    T = "search_records"
    kws = [k for k in (args.get("keywords") or []) if isinstance(k, str)]
    if not kws:
        return missing("keywords")
    hits = _search(data, kws, args.get("investigations") or (), args.get("fields") or (), int(args.get("limit") or 5))
    if not hits:
        return _out([], notes=["search_records: no hits"], state={"no_hits": kws})
    idx = data.search_index
    F = [_nasa_fact(data, T, x["acc"], x["unit"]) for x in hits]
    for f in F[:2]:
        f["lead"] = True
    lim = texts.LIMITS[T].format(n=idx["n"], k=idx["k"])
    F.append(fact(T, "limit", lim, ref="texts#search_limit", file="data/insights/evidence.json", key="records",
                  link=data.link("data/insights/evidence.json"), limit=True))
    P = [panel("quotes", "NASA record sentences that use these words", QUOTE_COLS,
               [_quote_row(data, x["acc"], x["unit"]) for x in hits], note=lim)]
    return _out(F, P)


# ---------------------------------------------------------------- 7.7 equipment_research
def equipment_matches(data, kind):
    out = []
    for acc, r in data.vocab["investigations"].items():
        role = r["row"]["fire_safety_role"].lower()
        focus = r["row"]["research_focus"].lower()
        ok = {"detection": "detection" in role or "detection" in focus or "smoke_soot" in focus,
              "suppression": "suppression" in role or "suppression" in focus,
              "material_selection": "prevention" in role,
              "ventilation": "flame_spread" in focus or "flammability_boundary" in focus}[kind]
        if ok:
            out.append(acc)
    return sorted(out, key=lambda a: int(a.split("-")[1]))


def equipment_research(args, data):
    kind = args.get("kind")
    if kind not in texts.EQUIPMENT:
        return missing("kind")
    T = "equipment_research"
    e = texts.EQUIPMENT[kind]
    accs = equipment_matches(data, kind)
    qwords = _joined([f"{data.needs[q]['name']} ({q})" for q in e["questions"]])
    F = [fact(T, "statement", texts.T["equip_list"].format(label=e["label"], questions=qwords,
              list=", ".join(f"{data.name(a)} ({a})" for a in accs)), ref=f"investigations.csv#rule/{kind}",
              file="data/catalog/investigations.csv", key=f"rule {kind}",
              link=data.link("data/catalog/investigations.csv"), invs=accs, lead=True)]
    counted = Counter(r["need_id"] for r in data.csv("need_tests") if r["objective_link"] == "stated")
    for q in e["questions"]:
        F.append(fact(T, "count", texts.T["equip_need"].format(need=data.needs[q]["name"], nid=q, n=counted.get(q, 0)),
                      ref=f"need_tests.csv#{q}/stated", file="data/pipeline/need_tests.csv", key=f"need_id={q}",
                      link=data.link("data/pipeline/need_tests.csv"), lead=(q == e["questions"][0] and False)))
    hits = _search(data, e["keywords"], accs, (), 6)
    F += [_nasa_fact(data, T, x["acc"], x["unit"]) for x in hits]
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#equipment_limit", file="ai/assistant/texts.py",
                  key="LIMITS.equipment_research", link=data.link("ai/assistant/texts.py"), limit=True))
    if len(F) > 2:
        F[1]["lead"] = True
    P = [panel("quotes", f"Record sentences: {e['label']}", QUOTE_COLS, [_quote_row(data, x["acc"], x["unit"]) for x in hits],
               note=texts.LIMITS[T]),
         panel("ranking", f"Investigations the team's rule links to {e['label'].lower()}",
               [col("investigation", "investigation"), col("accession", "accession"), col("role", "fire-safety role"),
                col("focus", "research focus"), col("record", "record", "link")],
               [{"investigation": data.name(a), "accession": a,
                 "role": data.vocab["investigations"][a]["row"]["fire_safety_role"],
                 "focus": data.vocab["investigations"][a]["row"]["research_focus"],
                 "record": {"text": a, "href": data.psi_url(a)}} for a in accs], note=texts.LIMITS[T], section="#all")]
    return _out(F, P)


# ---------------------------------------------------------------- 7.8 earth_applications
EARTH_RX = re.compile(r"\b(earth|terrestrial|industr\w*|engines?|power plants?|combustors?|emissions?|pollut\w*|"
                      r"buildings?|household|aircraft|wildfires?|furnaces?|turbines?|submarines?|automotive)\b", re.I)
EARTH_NOT = re.compile(r"\bfar from earth\b|\bas they do on earth\b", re.I)


def earth_units(data, invs=()):
    out = []
    for acc in sorted(data.evidence, key=lambda a: int(a.split("-")[1])):
        if invs and acc not in invs:
            continue
        for u in data.evidence[acc]["units"]:
            if u["field"] == "researchImpacts" and u.get("quotable") and EARTH_RX.search(u["text"]) \
                    and not EARTH_NOT.search(u["text"]):
                out.append((acc, u))
    return out


def earth_applications(args, data):
    T = "earth_applications"
    units = earth_units(data, [a for a in args.get("investigations") or [] if a in data.evidence])
    F = [_nasa_fact(data, T, acc, u) for acc, u in units[:8]]
    for f in F[:2]:
        f["lead"] = True
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#earth_limit", file="ai/assistant/texts.py",
                  key="LIMITS.earth_applications", link=data.link("ai/assistant/texts.py"), limit=True))
    P = [panel("quotes", "What the PSI records say about applications on Earth", QUOTE_COLS,
               [_quote_row(data, a, u) for a, u in units], note=texts.LIMITS[T])]
    return _out(F, P)


# ---------------------------------------------------------------- 7.10 criteria
CRIT_TYPES = ("acceptance_criterion", "requirement", "definition", "design_value", "monitoring_range", "exposure_limit")


def criteria(args, data):
    T = "criteria"
    qs = [q for q in (args.get("questions") or []) if q in data.needs] or list(data.needs)
    F, rows, seen = [], [], set()
    fnd = data.csv("findings")
    refs = data.csv("need_references")
    for q in qs:
        k = 0
        for i, r in enumerate(fnd):
            if k >= 4:
                break
            if r["kind"] != "criterion" or q not in r["needs"].split(";") or not r["quote"] or r["item_id"] in seen:
                continue
            seen.add(r["item_id"])
            k += 1
            F.append(fact(T, "criterion", texts.T["criterion_quote"].format(ref=r["reference_id"], where=r["where"],
                          quote=r["quote"]), ref=f"findings.csv#{r['finding_id']}", file="data/pipeline/findings.csv",
                          line=i + 2, context=f"{data.needs[q]['name']} ({q})", link=r["url"] or data.link(
                              "data/pipeline/findings.csv", i + 2), quote=True))
            rows.append({"question": q, "document": r["reference_id"], "version": r["version"], "section": r["where"],
                         "text": r["quote"], "link": {"text": r["reference_id"], "href": r["url"]} if r["url"] else None})
        for i, r in enumerate(refs):
            if k >= 4:
                break
            if r["need_id"] != q or r["item_type"] not in CRIT_TYPES or r["item_id"] in seen:
                continue
            seen.add(r["item_id"])
            k += 1
            F.append(fact(T, "criterion", texts.T["criterion_text"].format(ref=r["reference_id"], where=r["where"],
                          text=r["text"].rstrip(".") + "."), ref=f"need_references.csv#{r['item_id']}",
                          file="data/pipeline/need_references.csv", line=i + 2,
                          context=f"{data.needs[q]['name']} ({q})", link=r["url"] or data.link(
                              "data/pipeline/need_references.csv", i + 2)))
            rows.append({"question": q, "document": r["reference_id"], "version": r["version"], "section": r["where"],
                         "text": r["text"], "link": {"text": r["reference_id"], "href": r["url"]} if r["url"] else None})
    for f in F[:2]:
        f["lead"] = True
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#criteria_limit", file="ai/assistant/texts.py",
                  key="LIMITS.criteria", link=data.link("ai/assistant/texts.py"), limit=True))
    P = [panel("criteria", "Criteria in NASA documents", [col("question", "question"), col("document", "document"),
               col("version", "version"), col("section", "section"), col("text", "text"), col("link", "link", "link")],
               rows, note=texts.LIMITS[T], section="#criteria")]
    return _out(F, P)


# ---------------------------------------------------------------- 7.10a published_results (added 15 November)
RESULTS_FILE = "data/pipeline/results_by_need.json"
RESULT_GROUPS = ("at_environment", "about_a_stated_condition", "stated_without_these_conditions")  # not other_conditions
RESULTS_PER_QUESTION, RESULTS_PER_TURN = 4, 6


def _printed(pv):
    """One printed value as the file holds it: quantity (with column and row label), value as printed, unit."""
    q = " ".join(x for x in (pv.get("quantity") or pv.get("path") or "", pv.get("column") or "") if x).replace("_", " ")
    lbl = pv.get("material_as_printed") or pv.get("row_label") or ""
    return {"quantity": q + (f" ({lbl})" if lbl else ""), "value": pv.get("value_as_printed"), "unit": pv.get("unit")}


def _item_invs(doc, item_id):
    inv = (doc["items"].get(item_id) or {}).get("investigation")
    inv = [inv] if isinstance(inv, str) else inv or []
    return [a for a in inv if isinstance(a, str)]


def published_results(args, data):
    """Quoted results of NASA's experiments for the environment's scenario and the questions, in the order of
    data/pipeline/results_by_need.json (the data role's fixed rule; DESIGN.md 7.10a)."""
    e = args.get("env") or {}
    sid = e.get("scenario_id")
    if not sid:
        return missing("env.scenario_id")
    T = "published_results"
    doc = data.json(RESULTS_FILE)
    meta = doc["_meta"]
    glabel = {g["id"]: g["label"] for g in meta["order_rule"]["groups"]}
    klabel = meta["result_kind"]["labels"]
    blocks = {n["block_id"]: n for s in doc["scenarios"] for n in s["needs"]}
    scen = next((s for s in doc["scenarios"] if s["id"] == sid), None)
    if scen is None:
        return _out([], notes=[f"published_results: no scenario {sid} in {RESULTS_FILE}"])
    qs = [q for q in (args.get("questions") or []) if f"{sid}__{q}" in blocks] or [n["need_id"] for n in scen["needs"]]
    per_q = min(RESULTS_PER_QUESTION, max(1, math.ceil(RESULTS_PER_TURN / len(qs))))
    envl = e.get("label") or scen["label"]
    F, rows, seen = [], [], set()
    link_flat = data.link("data/pipeline/results_flat.csv")
    for q in qs:
        b = blocks[f"{sid}__{q}"]
        bid = b["block_id"]
        h = b["headline"]["fields"]
        ctx = f"{b['need']} ({q})"
        F.append(fact(T, "count", texts.T["result_counts"].format(nid=q, env=envl, n=h["n_tagged"],
                      v=h["n_with_values"], a=h["n_at"], b=h["n_about"], c=h["n_without"]),
                      ref=f"results_by_need.json#{bid}/headline", file=RESULTS_FILE, key=f"{bid}.headline.fields",
                      context=ctx,
                      link=data.link(RESULTS_FILE), lead=not F, what="a count of quoted results (team's computation)"))
        found = b["found"]
        picked = []
        for part in ("entries", "entries_tagged_for_all_questions"):
            if part == "entries_tagged_for_all_questions" and len(picked) >= 2:
                break
            for i, en in enumerate(found.get(part) or []):
                if len(picked) >= per_q or len(seen) >= RESULTS_PER_TURN:
                    break
                if en["group"] not in RESULT_GROUPS or en["finding_id"] in seen \
                        or not doc["findings"][en["finding_id"]].get("quote"):  # a result held without a quote is left out
                    continue
                seen.add(en["finding_id"])
                picked.append((part, i, en))
        for part, i, en in picked:
            fd = doc["findings"][en["finding_id"]]
            src = en["source"]
            kind = en.get("result_kind")
            rel = en.get("relation")
            text = texts.T["result_quote"].format(
                kind=(klabel[kind] + " ") if kind in klabel else "", doc=src["document_id"], where=src["where"],
                relation=texts.T["result_relation"].format(relation=rel) if rel else "", quote=fd["quote"],
                env=envl, group=glabel[en["group"]][:1].lower() + glabel[en["group"]][1:])
            F.append(fact(T, "published_result", text, ref=f"results_by_need.json#{bid}/{en['finding_id']}",
                          file=RESULTS_FILE, key=f"{bid}.found.{part}[{i}]", context=ctx,
                          link=src.get("url") or data.link(RESULTS_FILE), quote=True,
                          invs=_item_invs(doc, en["item_id"]), what="a value in the quoted result"))
            pv = [_printed(x) for x in fd.get("printed_values") or []]
            rows.append({"question": q, "investigation": f"{src['document_id']}: {src['title']}", "field": src["where"],
                         "sentence": fd["quote"], "kind": klabel.get(kind, "").rstrip(":") or (kind or "not labelled"),
                         "relation": rel, "group": glabel[en["group"]],
                         "values": [f"{x['quantity']}: {x['value']}" + (f" {x['unit']}" if x["unit"] and not str(
                             x["value"]).endswith(x["unit"]) else "") for x in pv],
                         "printed_values": pv, "finding_id": en["finding_id"],
                         "record": {"text": src["document_id"], "href": src["url"]} if src.get("url") else None})
        if not picked:
            F.append(fact(T, "count", texts.T["result_none"].format(nid=q, env=envl),
                          ref=f"results_by_need.json#{bid}/none", file=RESULTS_FILE, key=f"{bid}.found", context=ctx,
                          link=data.link(RESULTS_FILE)))
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#published_results_limit", file="ai/assistant/texts.py",
                  key="LIMITS.published_results", link=data.link("ai/assistant/texts.py"), limit=True))
    P = [panel("quotes", "What NASA's documents report for this question (quoted)",
               [col("question", "question"), col("investigation", "document"), col("field", "place"),
                col("sentence", "quote"), col("values", "printed values", "list"), col("kind", "kind of result"),
                col("relation", "experiment"), col("group", "team's group"), col("record", "source", "link")],
               rows, note=texts.LIMITS["published_results_panel"].format(limit=texts.LIMITS[T], url=link_flat))]
    return _out(F, P)


# ---------------------------------------------------------------- 7.11 files_of_test
def files_of_test(args, data):
    tid = data.vocab["test_ids"].get(str(args.get("test_id") or "").lower())
    if not tid:
        return missing("test_id")
    T = "files_of_test"
    rows = [(i, r) for i, r in enumerate(data.csv("test_files")) if r["test_id"] == tid]
    src = "data/pipeline/test_files.csv"
    F = []
    if not rows:
        F.append(fact(T, "file_group", texts.T["files_none"].format(test=tid), ref=f"test_files.csv#{tid}", file=src,
                      link=data.link(src), lead=True))
    by_level = OrderedDict()
    for lvl in ("test", "day_or_session"):
        sel = [r for _, r in rows if r["link_level"] == lvl]
        if sel:
            by_level[lvl] = (sum(int(r["files"]) for r in sel), sum(int(r["bytes"]) for r in sel))
    for lvl, (n, b) in by_level.items():
        line = next(i for i, r in rows if r["link_level"] == lvl) + 2
        F.append(fact(T, "file_group", texts.T["files_level"].format(files=n, size=_size(b), test=tid, level=lvl),
                      ref=f"test_files.csv#{tid}/{lvl}", file=src, line=line, link=data.link(src, line),
                      lead=len([f for f in F if f["lead"]]) < 1))
    kinds = Counter()
    for _, r in rows:
        kinds[r["kind"]] += int(r["files"])
    if kinds:
        F.append(fact(T, "file_group", texts.T["files_kinds"].format(kinds=", ".join(
            f"{k.replace('_', ' ')} {v}" for k, v in sorted(kinds.items(), key=lambda x: (-x[1], x[0])))),
            ref=f"test_files.csv#{tid}/kinds", file=src, link=data.link(src)))
    F.append(fact(T, "limit", texts.LIMITS[T], ref="texts#files_limit", file="ai/assistant/texts.py",
                  key="LIMITS.files_of_test", link=data.link("ai/assistant/texts.py"), limit=True))
    groups = {(g["investigation_id"], g["suffix_code"]): g for g in data.csv("raw_file_groups")}
    prow = []
    for _, r in rows:
        g = groups.get((r["investigation_id"], r["suffix_code"])) or {}
        prow.append({"level": r["link_level"], "kind": r["kind"], "suffix": g.get("suffix_meaning") or r["suffix_code"],
                     "files": int(r["files"]), "size": _size(r["bytes"]), "example": g.get("example_name")})
    P = [panel("files", f"Raw files that name {tid}", [col("level", "link level"), col("kind", "kind"),
               col("suffix", "suffix meaning"), col("files", "files", "number"), col("size", "size"),
               col("example", "example name")], prow, note=texts.LIMITS[T], section="#piles")]
    return _out(F, P)


# ---------------------------------------------------------------- 7.13 investigation_card
def investigation_card(args, data):
    acc = args.get("accession")
    inv = data.vocab["investigations"].get(acc)
    if not inv:
        return missing("accession")
    T = "investigation_card"
    r = inv["row"]
    line = data.inv_lines.get(acc)
    rec = data.evidence.get(acc) or {}
    title = rec.get("title") or r["investigation_name"]
    ai = texts.T["card_ai"] if r.get("verification_status") == "ai_extracted" else ""
    tpl = texts.T["card"] if (r.get("test_count") or "").strip() else texts.T["card_no_tests"]
    F = [fact(T, "card", tpl.format(name=data.name(acc), acc=acc, title=title, platform=r["platform"] or "not stated",
              period=r["operation_period"] or "not stated", tests=r.get("test_count"), ai=ai),
              ref=f"investigations.csv#{acc}", file="data/catalog/investigations.csv", line=line,
              link=data.link("data/catalog/investigations.csv", line), invs=[acc], lead=True)]
    cards = {c["investigation_id"]: c for c in data.json("data/insights/cards.json")}
    for i, kp in enumerate((cards.get(acc) or {}).get("key_points") or []):
        F.append(fact(T, "card", kp["text"], ref=f"cards.json#{acc}/key_points/{i}", file="data/insights/cards.json",
                      key=f"[{acc}].key_points[{i}]", link=data.psi_url(acc), quote=True, invs=[acc],
                      # the record field the key point quotes ('PSI-10.hypothesis'), so the aim/hypothesis frame
                      # check applies to it as to a record sentence (added after the grounding audit of 15 Nov)
                      field=(str(kp.get("source") or "").split(".", 1)[1:] or [None])[0]))
    rows = [{"name": k, "value": v} for k, v in (("investigation", r["investigation_name"]), ("accession", acc),
            ("platform", r["platform"]), ("operations", r["operation_period"]), ("tests in catalog", r["test_count"]),
            ("fire-safety role", r["fire_safety_role"]), ("research focus", r["research_focus"]),
            ("dataset DOI", r["dataset_doi"]), ("record", r["psi_url"]), ("catalog values", r["verification_status"]))]
    P = [panel("card", f"{data.name(acc)} ({acc})", [col("name", "field"), col("value", "value")], rows,
               note=ai.strip(" ()") or None, section="#all")]
    return _out(F, P)


# ---------------------------------------------------------------- 7.14 explain
def _build_glossary(data):
    E = []

    def add(aliases, text, file, key):
        E.append({"aliases": [a.lower().strip() for a in aliases if a], "text": text, "file": file, "key": key})
    nmeta = data.json("pipeline/spec/needs.json")["_meta"]
    for q, n in data.needs.items():
        add([q, n["name"]], f"{n['name']} ({q}): {n['question']} {n.get('reading') or ''}".strip(),
            "pipeline/spec/needs.json", f"needs[{q}]")
    allvars = dict(data.variables.get("variables", {}))
    allvars.update(data.variables.get("derived", {}) if isinstance(data.variables.get("derived"), dict) else {})
    for v, d in allvars.items():
        if not isinstance(d, dict) or not d.get("meaning"):
            continue
        unit = d.get("unit")
        txt = d["meaning"].rstrip(".") + (f", in {unit}." if unit and "|" not in unit and "materials.json" not in unit else ".")
        if d.get("formula"):
            txt += f" Formula: {d['formula']}."
        add([v, v.replace("_", " "), _var_words(v)], txt, "pipeline/spec/variables.json", f"variables.{v}")
    for aliases, key in ((["counted test", "usable", "counted", "counted tests"], "reading_rule"),
                         (["objective link", "stated", "not stated"], "stated_by_rule")):
        if nmeta.get(key):
            add(aliases, nmeta[key], "pipeline/spec/needs.json", f"_meta.{key}")
    cov = data.json("pipeline/spec/coverage.json")["_meta"]
    add(["oxidizer stream", "inverse flame", "o2 basis", "oxygen basis", "burner stream"], cov["o2_basis_rule"],
        "pipeline/spec/coverage.json", "_meta.o2_basis_rule")
    ab = data.cfg.get("_about") or {}
    add(["score", "ranking", "weights", "team score", "rank"], f"{ab.get('what', '')} Formula: {ab.get('formula', '')}.",
        "scoring/scoring_config.json", "_about")
    mr = data.json("data/insights/model_readiness.json")
    add(["readiness", "indicative", "too few", "readiness verdict", "verdict"], mr["verdict_rule"],
        "data/insights/model_readiness.json", "verdict_rule")
    piles = data.piles
    if "lunar_habitat" in piles:
        doc, rel = piles["lunar_habitat"]
        add(["no record in psi", "pile 3", "third pile", "no record"], doc["pile3_meaning"], rel, "pile3_meaning")
    for pid, p in data.vocab["presets"].items():
        if p.get("note"):
            add([pid, p["label"], pid.replace("_", " ")], p["note"], "pipeline/spec/scenarios.json", f"scenarios[{pid}].note")
    return E


def explain(args, data):
    term = (args.get("term") or "").strip()
    if not term:
        return missing("term")
    T = "explain"
    t = re.sub(r"\s+", " ", term.lower()).strip(" ?.'\"")
    words = [w for w in re.findall(r"[a-z0-9]+", t) if w not in checks._STOP and len(w) > 2]
    hit = next((e for e in data.glossary if t in e["aliases"]), None)
    if hit is None and words:
        hit = next((e for e in data.glossary if any(all(w in a for w in words) for a in e["aliases"])), None)
    if hit is None:
        return _out([], notes=["explain: no glossary entry"], state={"no_term": term})
    data.files_read.add(hit["file"])
    sents = checks.sentences_of(hit["text"]) or [hit["text"]]
    F = [fact(T, "definition", s.strip(), ref=f"{hit['file']}#{hit['key']}/{i}", file=hit["file"], key=hit["key"],
              link=data.link(hit["file"]) if not hit["file"].startswith("web/dist") else data.link(hit["file"]),
              lead=i < 2) for i, s in enumerate(sents[:3]) if s.strip()]
    P = [panel("definition", f"Definition: {term}"[:120], [col("text", "text")], [{"text": f["text"]} for f in F],
               note=None)]
    return _out(F, P)


# ---------------------------------------------------------------- registry and run
TOOLS = OrderedDict([
    ("rank_investigations", (rank_investigations, ["scoring/scoring_config.json", "data/catalog/investigations.csv",
                                                   "data/catalog/configurations.csv"])),
    ("counts_per_question", (counts_per_question, ["data/pipeline/evidence/*.json", "data/pipeline/scenario_needs.csv",
                                                   "data/pipeline/atmosphere_cells.csv", "data/pipeline/answers/*.json"])),
    ("tested_range", (tested_range, ["data/pipeline/tests.csv", "data/insights/model_readiness.json"])),
    ("where_the_data_are", (where_the_data_are, ["web/dist/data/piles/*.json or web/raw_piles.py",
                                                 "data/pipeline/need_gap_states.csv", "data/pipeline/retrieval_queue.csv"])),
    ("tests_table", (tests_table, ["data/pipeline/scenario_tests.csv", "data/pipeline/need_tests.csv",
                                   "data/pipeline/tests.csv", "pipeline/spec/needs.json"])),
    ("modelling_data", (modelling_data, ["data/insights/model_readiness.json", "pipeline/spec/needs.json",
                                         "pipeline/spec/variables.json", "data/pipeline/need_gap_states.csv",
                                         "data/pipeline/retrieval_queue.csv", "data/pipeline/need_tests.csv",
                                         "data/pipeline/tests.csv"])),
    ("equipment_research", (equipment_research, ["data/catalog/investigations.csv", "data/insights/evidence.json",
                                                 "data/pipeline/need_tests.csv", "pipeline/spec/needs.json"])),
    ("earth_applications", (earth_applications, ["data/insights/evidence.json"])),
    ("search_records", (search_records, ["data/insights/evidence.json"])),
    ("criteria", (criteria, ["data/pipeline/findings.csv", "data/pipeline/need_references.csv"])),
    ("published_results", (published_results, ["data/pipeline/results_by_need.json"])),  # added 15 November
    ("files_of_test", (files_of_test, ["data/pipeline/test_files.csv", "data/pipeline/raw_file_groups.csv"])),
    ("investigation_card", (investigation_card, ["data/insights/cards.json", "data/catalog/investigations.csv",
                                                 "data/insights/evidence.json"])),
    ("explain", (explain, ["pipeline/spec/needs.json", "pipeline/spec/variables.json", "pipeline/spec/coverage.json",
                           "pipeline/spec/scenarios.json", "scoring/scoring_config.json",
                           "data/insights/model_readiness.json"])),
])


def run_tool(name, args, data):
    fn = TOOLS[name][0]
    return fn(args or {}, data)


def run(steps, data):
    """Run the planned tools in order; number facts F1.. and panels p1..; link panels to their facts."""
    facts, panels, trace, notes, state = [], [], [], [], {}
    data.files_read = set()
    for st in steps:
        t0 = time.monotonic()
        try:
            out = run_tool(st["tool"], st["args"], data)
        except Exception as e:  # noqa: BLE001 - one failing tool does not end the turn
            out = _out([], notes=[f"{st['tool']} failed: {type(e).__name__}: {e}"])
        start = len(facts)
        for f in out["facts"]:
            f = dict(f)
            f["id"] = f"F{len(facts) + 1}"
            facts.append(f)
        ids = [f["id"] for f in facts[start:]]
        for p in out["panels"]:
            p = dict(p)
            p.pop("fact_refs", None)
            p["id"] = f"p{len(panels) + 1}"
            p["fact_ids"] = ids
            panels.append(p)
        notes += out["notes"]
        for k, v in (out.get("state") or {}).items():
            state.setdefault(k, v)
        trace.append({"tool": st["tool"], "ms": int((time.monotonic() - t0) * 1000), "facts": len(out["facts"]),
                      "panels": len(out["panels"])})
    return {"facts": facts, "panels": panels, "trace": trace, "notes": notes, "state": state,
            "files": sorted(data.files_read)}


def writer_facts(facts, limit=MAX_WRITER_FACTS):
    """At most `limit` facts for the writer: lead facts first, then plan order; limit facts always included
    (DESIGN.md 6.1). Returned in plan order."""
    lim = [f for f in facts if f["limit"]]
    lead = [f for f in facts if f["lead"] and not f["limit"]]
    rest = [f for f in facts if not f["lead"] and not f["limit"]]
    room = max(limit - min(len(lim), limit // 3), 0)
    chosen = (lead + rest)[:room]
    chosen += lim[:limit - len(chosen)]
    keep = {f["id"] for f in chosen}
    return [f for f in facts if f["id"] in keep]
