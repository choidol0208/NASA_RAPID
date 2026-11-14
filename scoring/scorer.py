#!/usr/bin/env python3
# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
# Challenge 2026 hackathon (2026-11-14). Scores are the team's ranking method, not NASA's.
"""Rank PSI test configurations by similarity to a user scenario.

The user may give a rough query ("ISS", "달 기지 면직물" = Korean for "lunar base cotton fabric", "smoke detector") or a
structured dict. The query is interpreted in three layers, later ones winning:
    defaults  <  preset (e.g. ISS)  <  words and numbers in the text  <  explicit fields
Every value that did not come from the user is listed in `assumptions`, so the
dashboard can show what was assumed and let the user change it.

Usage (CLI):
    python3 -m scoring.scorer "lunar habitat cotton fabric"
    python3 -m scoring.scorer '{"preset": "iss", "fuel": "PMMA", "concern": "prevention"}' --json

Usage (code):
    from scoring.scorer import rank
    out = rank("ISS")            # dict: status, scenario, assumptions, warnings, results
    out["results"][0]["investigation_id"]

All rules and numbers live in scoring/scoring_config.json. Standard library only.
"""
import csv
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DEFAULT_CATALOG = os.path.join(ROOT, "data", "catalog")
DEFAULT_CONFIG = os.path.join(HERE, "scoring_config.json")
DIMS = ["o2", "pressure", "flow", "fuel", "geometry", "role", "diluent"]
UNITS_TO_KPA = {"kpa": 1.0, "psi": 6.89476, "psia": 6.89476, "atm": 101.325, "bar": 100.0, "mmhg": 0.133322}


# ------------------------------------------------------------------------------ loading
def load_config(path=None):
    with open(path or DEFAULT_CONFIG, encoding="utf-8") as fh:
        return json.load(fh)


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _r(x, n):
    """Round half up after snapping to 9 decimals, so the JavaScript port (web/scorer.js)
    rounds identically despite last-bit differences between math libraries."""
    m = 10 ** n
    return math.floor(round(x, 9) * m + 0.5) / m


def _split(v):
    return [p.strip().lower() for p in re.split(r"[;,]", v or "") if p.strip()]


def load_catalog(catalog_dir=None):
    d = catalog_dir or DEFAULT_CATALOG
    with open(os.path.join(d, "investigations.csv"), encoding="utf-8") as fh:
        inv = {r["investigation_id"]: r for r in csv.DictReader(fh)}
    with open(os.path.join(d, "configurations.csv"), encoding="utf-8") as fh:
        cfgs = list(csv.DictReader(fh))
    for c in cfgs:
        c["_inv"] = inv[c["investigation_id"]]
    return inv, cfgs


# ------------------------------------------------------------------------ interpretation
def _has(text, key):
    key = key.lower()
    if re.fullmatch(r"[a-z0-9 \-/+.]+", key.strip()):
        return re.search(r"(?<![a-z0-9])" + re.escape(key.strip()) + r"(?![a-z0-9])", text) is not None
    if len(key.strip()) == 1:  # one Korean syllable: must start a short token
        return any(t.startswith(key.strip()) and len(t) <= 3 for t in text.split())
    return key in text


def _any(text, keys):
    return any(_has(text, k) for k in keys)


def _spans(text, key):
    """Character spans where key matches text, by the same rules as _has."""
    key = key.lower()
    k = key.strip()
    if re.fullmatch(r"[a-z0-9 \-/+.]+", k):
        return [m.span() for m in re.finditer(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text)]
    if len(k) == 1:
        return [m.span() for m in re.finditer(r"\S+", text) if m.group(0).startswith(k) and len(m.group(0)) <= 3]
    out, i = [], text.find(key)
    while i >= 0:
        out.append((i, i + len(key)))
        i = text.find(key, i + 1)
    return out


# Korean input words in the patterns: 산소 = oxygen, 농도 = concentration.
NUMBER_PATTERNS = [r"(\d+(?:\.\d+)?)\s*%\s*(?:o2|oxygen|산소)(?![a-z0-9])",
                   r"(?<![a-z0-9])(?:o2|oxygen|산소)\s*(?:농도)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?",
                   r"(\d+(?:\.\d+)?)\s*(kpa|psia|psi|atm|bar|mmhg)\b", r"(\d+(?:\.\d+)?)\s*(cm/s|mm/s|m/s)"]


def not_understood(query, cfg):
    """Words of the query that no keyword, preset alias or number pattern reads, joined into phrases
    ("battery enclosure"). Words in keywords.generic ("for", "fire", "system") are left out. The
    ranking ignores these words; the page says so (warning not_understood). Scores do not change."""
    text = str((query.get("text") if isinstance(query, dict) else query) or "")
    t = " " + text.lower().strip() + " "
    kw = cfg["keywords"]
    keys = [a for p in cfg["presets"].values() for a in p["aliases"]]
    for group in ("gravity", "flow_state", "concern", "diluent"):
        keys += [k for v in kw[group].values() for k in v]
    keys += [k for m in kw["materials"] for k in m["keys"]]
    for group in ("thin", "thick", "rod", "out_of_scope", "generic"):
        keys += kw.get(group, [])
    covered = [s for k in keys for s in _spans(t, k)]
    covered += [m.span() for p in NUMBER_PATTERNS for m in re.finditer(p, t)]
    phrases, cur = [], []
    for m in re.finditer(r"\S+", t):
        word = m.group(0).strip(",.;:!?()\"'")
        if not word or any(a < m.end() and m.start() < b for a, b in covered):
            if cur:
                phrases.append(" ".join(cur))
                cur = []
            continue
        cur.append(word)
    if cur:
        phrases.append(" ".join(cur))
    return phrases


def interpret(query, cfg):
    """Turn a rough or structured query into a scenario dict plus assumptions."""
    if isinstance(query, dict):
        q = dict(query)
        text = str(q.pop("text", "") or "")
    else:
        q, text = {}, str(query or "")
    t = " " + text.lower().strip() + " "
    kw = cfg["keywords"]
    sc, src = {}, {}

    def put(field, value, source):
        if value is None or value == "":
            return
        sc[field] = value
        src[field] = source

    # 1) preset (explicit, else first alias found in text)
    preset = q.get("preset")
    if not preset:
        for name, p in cfg["presets"].items():
            if _any(t, p["aliases"]):
                preset = name
                break
    if preset:
        if preset not in cfg["presets"]:
            raise ValueError(f"unknown preset: {preset}")
        for k, v in cfg["presets"][preset]["values"].items():
            put(k, v, f"preset:{preset}")
        sc["preset"] = preset

    # 2) words in the text
    for g, keys in kw["gravity"].items():
        if _any(t, keys):
            put("gravity", g, "text")
            break
    for state in ("quiescent", "opposed", "concurrent", "ventilated"):
        if _any(t, kw["flow_state"][state]):
            put("flow_state", state, "text")
            break
    for concern in ("detection", "suppression", "prevention"):
        if _any(t, kw["concern"][concern]):
            put("concern", concern, "text")
            break
    for dil, keys in kw["diluent"].items():
        if _any(t, keys):
            put("diluent", dil, "text")
            break
    mat = _match_material(t, kw["materials"])
    if mat:
        for k, v in mat.items():
            if k != "keys":
                put(k, v, "text")
    if _any(t, kw["thin"]):
        put("thermal_regime", "thin", "text")
    elif _any(t, kw["thick"]):
        put("thermal_regime", "thick", "text")
    if _any(t, kw["rod"]):
        put("sample_geometry", "rod", "text")
    # numbers with units ("o2" must stand alone: "CO2 30%" is not 30% oxygen; 산소 = oxygen, 농도 = concentration)
    m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:o2|oxygen|산소)(?![a-z0-9])", t) or \
        re.search(r"(?<![a-z0-9])(?:o2|oxygen|산소)\s*(?:농도)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?", t)
    if m:
        put("o2_pct", float(m.group(1)), "text")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(kpa|psia|psi|atm|bar|mmhg)\b", t)
    if m:
        put("pressure_kpa", _r(float(m.group(1)) * UNITS_TO_KPA[m.group(2)], 1), "text")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(cm/s|mm/s|m/s)", t)
    if m:
        v = float(m.group(1)) * {"cm/s": 1.0, "mm/s": 0.1, "m/s": 100.0}[m.group(2)]
        put("flow_cms", v, "text")
    out_of_scope = _any(t, kw["out_of_scope"])

    # 3) explicit fields win
    if q.get("fuel"):
        mat = _match_material(" " + str(q["fuel"]).lower() + " ", kw["materials"])
        if mat:
            for k, v in mat.items():
                if k != "keys":
                    put(k, v, "input")
        else:
            put("fuel_material", str(q["fuel"]).lower(), "input")
    for k in ("o2_pct", "pressure_kpa", "flow_cms"):
        if q.get(k) is not None:
            put(k, float(q[k]), "input")
    for k in ("flow_state", "fuel_phase", "fuel_class", "fuel_material", "melt_behavior", "thermal_regime",
              "sample_geometry", "concern", "diluent", "gravity"):
        if q.get(k):
            put(k, q[k], "input")
    if "flow_state" not in sc and sc.get("flow_cms") is not None:
        put("flow_state", "quiescent" if sc["flow_cms"] == 0 else "ventilated", "derived")
    if sc.get("flow_state") == "quiescent" and "flow_cms" not in sc:
        put("flow_cms", 0.0, "derived")
    if "concern" not in sc:
        put("concern", cfg["default_profile"], "default")
    if q.get("profile"):
        put("concern", q["profile"], "input")

    assumptions = [{"field": k, "value": sc[k], "source": s} for k, s in src.items()
                   if s.startswith("preset") or s in ("default", "derived")]
    informative = [k for k in sc if k != "preset" and src.get(k) in ("text", "input")] or \
        ([k for k in sc if src.get(k, "").startswith("preset")])
    return sc, src, assumptions, out_of_scope, informative


def _match_material(t, materials):
    for m in materials:  # list order = priority (specific first)
        if _any(t, m["keys"]):
            return m
    return None


# --------------------------------------------------------------------------- similarity
def _range(c, lo, hi):
    a, b = _f(c.get(lo)), _f(c.get(hi))
    if a is None and b is None:
        return None
    return (a if a is not None else b, b if b is not None else a)


def s_o2(x, c, p):
    # An inverse flame's O2 is the burner's oxidizer stream; the surrounding atmosphere is fuel and
    # inert gas. It is not an atmosphere a crew breathes, so it is never matched with the user's O2.
    if (c.get("o2_reference") or "") == "oxidizer_stream":
        return None
    r = _range(c, "o2_min_pct", "o2_max_pct")
    if r is None:
        return None
    lo, hi = r
    if lo <= x <= hi:
        return 1.0
    # Distance on the log of the O2 ratio (config "log_ratio"): oxygen acts through ratios of its
    # mole fraction, so 15 against 21% is a larger gap than 30 against 36% (scoring/MODEL_BASIS.md).
    if x > hi:
        return math.exp(-math.log(x / hi) / p["above_scale_ln"])
    if x <= 0:
        return 0.0
    return math.exp(-math.log(lo / x) / p["below_scale_ln"])


def _log_gauss(x, lo, hi, sigma, offset=0.0):
    if lo <= x <= hi:
        return 1.0
    near = lo if x < lo else hi
    z = math.log((x + offset) / (near + offset)) / sigma
    return math.exp(-0.5 * z * z)


def s_pressure(x, c, p):
    r = _range(c, "pressure_min_kpa", "pressure_max_kpa")
    return None if r is None else _log_gauss(x, r[0], r[1], p["sigma_ln"])


def _speed(v, c, sim):
    """Flow-speed similarity and the in-range signal for the outside_range warning.
    With one end not recorded (PSI-26: "up to 40 cm/s", the tunnel's limit, not a test value), a
    speed on the open side of that end is neither a match nor a miss: it scores unknown_value and
    raises no warning. Beyond the end it decays from unknown_value, so the score has no jump there."""
    a, b = _f(c.get("flow_min_cms")), _f(c.get("flow_max_cms"))
    if a is None and b is None:
        return None, None
    p = sim["flow_speed"]
    if a is None or b is None:
        end = b if a is None else a
        if (a is None and v <= end) or (b is None and v >= end):
            return sim["unknown_value"], None
        g = _log_gauss(v, end, end, p["sigma_ln"], p["offset_cms"])
        return sim["unknown_value"] * g, g
    s = _log_gauss(v, a, b, p["sigma_ln"], p["offset_cms"])
    return s, s


def s_flow(state, v, c, sim):
    cfgs = _split(c.get("flow_config"))
    s_cfg = None
    if state and cfgs:
        row = sim["flow_config_matrix"][state]
        s_cfg = max(row.get(k, 0.3) for k in cfgs)
    s_v = _speed(v, c, sim)[0] if v is not None else None
    parts = [x for x in (s_cfg, s_v) if x is not None]
    if not parts:
        return None
    return math.prod(parts) if len(parts) == 2 else parts[0]


def s_fuel(sc, c, p):
    phase, cls = sc.get("fuel_phase"), sc.get("fuel_class")
    mat, melt = sc.get("fuel_material"), sc.get("melt_behavior")
    cphase = (c.get("fuel_phase") or "").lower()
    if not cphase:
        return None
    if mat and mat.lower() in (c.get("fuel_material") or "").lower():
        return p["same_material"]
    if cls and cls in _split(c.get("fuel_class")):
        cmelt = (c.get("melt_behavior") or "").lower()
        if melt and cmelt and melt == cmelt:
            return p["same_class_same_melt"]
        return p["same_class"]
    if phase and phase == cphase:
        return p["same_phase"]
    if phase == "solid" and (c.get("surrogate_for") or "").lower() == "solid":
        return p["solid_surrogate"]
    if phase and {phase, cphase} == {"liquid", "gas"}:
        return p["liquid_gas"]
    return p["other"]


def s_geometry(sc, c, p):
    ug, ur = sc.get("sample_geometry"), sc.get("thermal_regime")
    cg, cr = _split(c.get("sample_geometry")), _split(c.get("thermal_regime"))
    if not cg:
        return None
    solid = set(p["solid_geometries"])
    user_solid = (sc.get("fuel_phase") == "solid") or (ug in solid) or (ur is not None)
    cfg_solid = bool(set(cg) & solid)
    if (user_solid and not cfg_solid) or (ug and not user_solid and cfg_solid):
        return p["phase_family_mismatch"]
    same_g = (ug in cg) if ug else None
    same_r = (ur in cr) if (ur and cr) else None
    if same_g and same_r is not False:
        return p["same_geometry"]
    if same_g and same_r is False:
        return p["same_geometry_other_regime"]
    if same_r:
        return p["other_geometry_same_regime"]
    if same_g is None and same_r is None:
        return None
    return p["solid_other"]


def s_role(concern, c, p):
    inv = c["_inv"]
    roles, focus = _split(inv.get("fire_safety_role")), _split(inv.get("research_focus"))
    if concern in roles:
        return p["same_axis"]
    if set(focus) & set(p["related_focus_by_axis"].get(concern, [])):
        return p["related_focus"]
    if "fundamental" in roles:
        return p["fundamental"]
    return p["other"]


def s_diluent(dil, c, p):
    cd = [x.lower() for x in _split(c.get("diluent"))]
    if not cd:
        return p["none"]
    if dil.lower() in cd:
        return p["same"]
    # Another inert: compared by molar heat capacity, the thermal effect of a diluent (scoring/MODEL_BASIS.md).
    cp = {k.lower(): v for k, v in (p.get("molar_cp_298K_kJ_per_kmolK") or {}).items()}
    u = cp.get(dil.lower())
    vals = [(min(u, cp[x]) / max(u, cp[x])) ** p.get("cp_ratio_exponent", 1) for x in cd if u is not None and x in cp]
    return max(vals) if vals else p["other_inert"]


def evidence(c, e):
    inv = c["_inv"]
    q = [e["data_availability"].get(inv.get("data_availability"), 0.5),
         e["mu_g_duration_class"].get(inv.get("mu_g_duration_class"), 0.5),
         e["verification_status"].get(inv.get("verification_status"), 0.7)]
    return e["base"] + e["span"] * sum(q) / len(q)


# ------------------------------------------------------------------------------ ranking
def _with_fallback(c, cfg):
    """Scoring-only defaults for unreported atmosphere (see atmosphere_fallback in the config)."""
    fb = cfg.get("atmosphere_fallback") or {}
    c2, used = dict(c), []
    if fb.get("o2_pct") is not None and _range(c, "o2_min_pct", "o2_max_pct") is None and \
            (fb.get("o2_applies_to") == "all" or c["investigation_id"] in fb.get("o2_applies_to", [])):
        c2["o2_min_pct"] = c2["o2_max_pct"] = fb["o2_pct"]
        used.append("O2")
    if fb.get("pressure_kpa") is not None and _range(c, "pressure_min_kpa", "pressure_max_kpa") is None and \
            c["investigation_id"] in fb.get("pressure_applies_to_investigations", []):
        c2["pressure_min_kpa"] = c2["pressure_max_kpa"] = fb["pressure_kpa"]
        used.append("pressure")
    return c2, used


def similarities(sc, c, cfg):
    """Raw similarity per active dimension (None = catalog value unknown)."""
    sim = cfg["similarity"]
    c, fallback = _with_fallback(c, cfg)
    S = {}
    if sc.get("o2_pct") is not None:
        S["o2"] = s_o2(sc["o2_pct"], c, sim["o2"])
    if sc.get("pressure_kpa") is not None:
        S["pressure"] = s_pressure(sc["pressure_kpa"], c, sim["pressure"])
    speed_in_range = None
    if sc.get("flow_state") or sc.get("flow_cms") is not None:
        S["flow"] = s_flow(sc.get("flow_state"), sc.get("flow_cms"), c, sim)
        if sc.get("flow_cms") is not None:
            speed_in_range = _speed(sc["flow_cms"], c, sim)[1]
    if any(sc.get(k) for k in ("fuel_phase", "fuel_class", "fuel_material")):
        S["fuel"] = s_fuel(sc, c, sim["fuel"])
    if sc.get("sample_geometry") or sc.get("thermal_regime"):
        S["geometry"] = s_geometry(sc, c, sim["geometry"])
    S["role"] = s_role(sc["concern"], c, sim["role"])
    if sc["concern"] == "suppression" and sc.get("diluent"):
        S["diluent"] = s_diluent(sc["diluent"], c, sim["diluent"])
    return S, fallback, speed_in_range, c


def score_config(sc, c, cfg, weights, raw_S, caps, assumed=()):
    """assumed: dimensions whose catalog value was filled by the atmosphere fallback ("o2", "pressure")."""
    sim = cfg["similarity"]
    S, unknown = {}, []
    for d, v in raw_S.items():
        if v is None:
            unknown.append(d)
            S[d] = min(sim["unknown_value"], caps.get(d, 1.0))
        else:
            S[d] = v
    w = {d: weights.get(d, 0.0) for d in S if weights.get(d, 0.0) > 0}
    total_w = sum(w.values()) or 1.0
    w = {d: x / total_w for d, x in w.items()}
    raw = sum(w[d] * S[d] for d in w)
    gate = 1.0
    g = cfg["gate"]
    for d in g["dimensions"]:
        if d in S and S[d] < g["min_similarity"]:
            if g.get("mode") == "ramp":
                gate = min(gate, g["factor"] + (1 - g["factor"]) * S[d] / g["min_similarity"])
            else:
                gate = min(gate, g["factor"])
    M = evidence(c, cfg["evidence"])
    score = 100.0 * M * gate * raw
    full = sum(v for k, v in weights.items() if v > 0 and (k != "diluent" or sc["concern"] == "suppression"))
    # Confidence counts only what was compared with a recorded value: an assumed (fallback) value
    # is scored, but it is not evidence that the configuration matches.
    known_w = sum(weights[d] for d in w if d not in unknown and d not in assumed)
    coverage = known_w / full if full else 0.0
    return dict(score=score, raw=raw, gate=gate, evidence=M, similarity=S, weights=w,
                unknown=unknown, coverage=coverage,
                contributions={d: w[d] * S[d] for d in w})


def _fmt_range(c, lo, hi, unit):
    # Text only. When one end is not recorded, say so ("up to 40 cm/s" in the PSI-26 record is
    # not "at 40 cm/s"). Similarity still uses _range, which treats the recorded end as both ends.
    a, b = _f(c.get(lo)), _f(c.get(hi))
    if a is None and b is None:
        return "not reported"
    if a is None:
        return f"up to {b:g}{unit}"
    if b is None:
        return f"at least {a:g}{unit}"
    return f"{a:g}{unit}" if a == b else f"{a:g}–{b:g}{unit}"


def _is_span(c, lo, hi):
    a, b = _f(c.get(lo)), _f(c.get(hi))
    return a is not None and b is not None and a < b


# How a number is worded by where it comes from (the catalog's o2_source, pressure_source, flow_source).
SOURCE_NOTE = {"record": "named in the PSI record, not a test value", "test_matrix": "from the test matrix, not individual tests",
               "team": "team reading, not in the table"}


def _fmt_value(c, var, label, lo, hi, unit, assumed):
    r = _fmt_range(c, lo, hi, unit)
    if assumed:  # filled in by the atmosphere fallback: never worded as "tested"
        return f"{label} not recorded, assumed {r}"
    note = SOURCE_NOTE.get(c.get(f"{var}_source") or "")
    return f"{label} {r}, {note}" if note else f"{label} tested {r}"


def _fmt_flow(c):
    r = _fmt_range(c, "flow_min_cms", "flow_max_cms", " cm/s")
    head = f"flow {c.get('flow_config') or 'n/a'}"
    if r == "not reported":
        return f"{head}, speed not reported"
    text = f"{head}, {r}" if r.startswith(("up to", "at least")) else f"{head} at {r}"
    note = SOURCE_NOTE.get(c.get("flow_source") or "")
    return f"{text}, {note}" if note else text


def explain(sc, c, s, cfg, fallback=(), speed_in_range=None):
    """Deterministic one-line reasons (no LLM)."""
    sim, W = s["similarity"], cfg["warnings"]
    labels = {"o2": "O2", "pressure": "pressure", "flow": "flow", "fuel": "fuel", "geometry": "sample shape",
              "role": "research purpose", "diluent": "diluent"}
    known = [d for d in s["contributions"] if d not in s["unknown"]]
    assumed = {"o2"} if "O2" in fallback else set()
    if "pressure" in fallback:
        assumed.add("pressure")
    # Reasons come from recorded values first; an assumed (not recorded) value is a reason only if nothing else is left.
    best = sorted(known, key=lambda d: (d in assumed, -s["contributions"][d]))[:2]
    gaps = sorted(known, key=lambda d: sim[d])[:1]
    detail = {
        # "tested" only for numbers from an experimental table; assumed, record and matrix values say so.
        "o2": _fmt_value(c, "o2", "O2", "o2_min_pct", "o2_max_pct", "%", "O2" in fallback),
        "pressure": _fmt_value(c, "pressure", "pressure", "pressure_min_kpa", "pressure_max_kpa", " kPa", "pressure" in fallback),
        "flow": _fmt_flow(c),
        "fuel": f"fuel {c.get('fuel_material')}",
        "geometry": f"{c.get('sample_geometry')} ({c.get('thermal_regime') or 'regime n/a'})",
        "role": f"role {c['_inv'].get('fire_safety_role')}",
        "diluent": f"diluent {c.get('diluent') or 'none'}",
    }
    why = "; ".join(f"{labels[d]} match {sim[d]:.2f} ({detail[d]})" for d in best)
    gap = "; ".join(f"{labels[d]} {sim[d]:.2f} ({detail[d]})" for d in gaps if sim[d] < 0.9)
    warns = []
    stream = (c.get("o2_reference") or "") == "oxidizer_stream"
    o2max = None if stream else _f(c.get("o2_max_pct"))
    if sc.get("o2_pct") is not None and o2max is not None and sc["o2_pct"] > o2max:
        warns.append({"code": "o2_above_result", "message": W["o2_above_result"].format(user=f"{sc['o2_pct']:g}", max=f"{o2max:g}")})
    thr = cfg.get("outside_range_threshold", 0.9)
    out = [labels[d] for d in known if d in ("o2", "pressure") and sim[d] < thr]
    if speed_in_range is not None and speed_in_range < thr:
        out.append("flow speed")
    if out:
        warns.append({"code": "outside_range", "message": W["outside_range"].format(dims=", ".join(out))})
    # pm decision 14:15: two true ranges compared side by side must not read as one test at both values.
    if "o2" in known and "pressure" in known and not ({"O2", "pressure"} & set(fallback)) \
            and _is_span(c, "o2_min_pct", "o2_max_pct") and _is_span(c, "pressure_min_kpa", "pressure_max_kpa"):
        warns.append({"code": "ranges_separate", "message": W["ranges_separate"]})
    if sc.get("fuel_phase") == "solid" and (c.get("fuel_phase") or "").lower() == "gas":
        warns.append({"code": "gas_for_solid", "message": W["gas_for_solid"]})
    if stream and "o2" in sim:
        warns.append({"code": "oxidizer_stream", "message": W["oxidizer_stream"]})
    missing = [d for d in s["unknown"] if not (stream and d == "o2")]  # O2 of a stream is recorded, just not comparable
    if missing:
        warns.append({"code": "not_reported", "message": W["not_reported"].format(dims=", ".join(labels[d] for d in missing))})
    if fallback:
        warns.append({"code": "fallback", "message": W["fallback"].format(dims=" and ".join(fallback))})
    if c["_inv"].get("platform") == "ground":
        warns.append({"code": "ground_analysis", "message": W["ground_analysis"]})
    return why, gap, warns


def rank(query, catalog_dir=None, config=None, top_k=None, weights_override=None, catalog=None):
    cfg = config if isinstance(config, dict) else load_config(config)
    inv, cfgs = catalog or load_catalog(catalog_dir)
    sc, src, assumptions, out_of_scope, informative = interpret(query, cfg)
    W = cfg["warnings"]
    unread = not_understood(query, cfg)
    base = {"scenario": {k: v for k, v in sc.items()}, "sources": src, "assumptions": assumptions,
            "config_version": cfg["version"], "not_understood": unread}
    unread_w = [{"code": "not_understood", "message": W["not_understood"].format(words=", ".join(f"'{p}'" for p in unread))}] if unread else []
    if out_of_scope:
        return dict(base, status="out_of_scope", warnings=[{"code": "out_of_scope", "message": W["out_of_scope"]}], results=[], ranking=[])
    if not informative:
        return dict(base, status="need_input", warnings=[{"code": "need_input", "message": W["need_input"]}] + unread_w, results=[], ranking=[])
    profile = sc["concern"] if sc["concern"] in cfg["profiles"] else cfg["default_profile"]
    weights = dict(cfg["profiles"][profile]["weights"])
    if weights_override:
        weights.update(weights_override)
    warnings = list(unread_w)
    g = sc.get("gravity")
    if g in ("lunar", "martian"):
        warnings.append({"code": "partial_gravity", "message": W["partial_gravity"]})
    elif g == "earth":
        warnings.append({"code": "earth_gravity", "message": W["earth_gravity"]})
    # Highest O2 of any surrounding atmosphere tested (oxidizer streams of inverse flames excluded).
    o2s = [(_f(c.get("o2_max_pct")), c) for c in cfgs
           if _f(c.get("o2_max_pct")) is not None and (c.get("o2_reference") or "") != "oxidizer_stream"]
    max_o2, max_c = max(o2s, key=lambda x: x[0])
    if sc.get("o2_pct") is not None and sc["o2_pct"] > max_o2:
        warnings.append({"code": "o2_above_all", "message": W["o2_above_all"].format(
            max_o2=f"{max_o2:g}", max_cfg=max_c["config_id"], ref=max_c.get("o2_reference") or "ambient")})
    if sc.get("preset") == "mars_habitat" and sc.get("o2_pct") is None:
        warnings.append({"code": "mars_atmosphere", "message": cfg["presets"]["mars_habitat"]["source"]})

    pre = []
    for c in cfgs:
        S, fallback, speed, c_eff = similarities(sc, c, cfg)
        pre.append((c, S, fallback, speed, c_eff))
    caps = {}
    for d in cfg["similarity"].get("unknown_cap_dims", []):
        known = [S[d] for _, S, _, _, _ in pre if d in S and S[d] is not None]
        if known:
            caps[d] = max(known)
    scored = []
    for c, S, fallback, speed, c_eff in pre:
        assumed = {{"O2": "o2", "pressure": "pressure"}[x] for x in fallback}
        s = score_config(sc, c, cfg, weights, S, caps, assumed)
        why, gap, warns = explain(sc, c_eff, s, cfg, fallback, speed)
        scored.append(dict(
            config_id=c["config_id"], investigation_id=c["investigation_id"], psi_accession=c["psi_accession"],
            config_label=c["config_label"], score=_r(s["score"], 1), raw=_r(s["raw"], 3), gate=_r(s["gate"], 3),
            evidence=_r(s["evidence"], 3), similarity={k: _r(v, 3) for k, v in s["similarity"].items()},
            contributions={k: _r(v, 3) for k, v in s["contributions"].items()},
            weights_used={k: _r(v, 3) for k, v in s["weights"].items()}, unknown_dims=s["unknown"],
            assumed_dims=fallback, coverage=_r(s["coverage"], 2), why=why, main_gap=gap, warnings=warns,
            psi_url=c["_inv"]["psi_url"], dataset_doi=c["_inv"]["dataset_doi"],
            key_findings=c.get("key_findings") or c["_inv"].get("key_findings"),
            has_1g_comparison=c["_inv"].get("has_1g_comparison") == "Y",
            verification_status=c["_inv"].get("verification_status")))
    scored.sort(key=lambda r: (-r["score"], -r["evidence"], -int(r["has_1g_comparison"]), r["config_id"]))
    best, others = {}, {}
    for r in scored:  # one configuration per investigation
        if r["investigation_id"] not in best:
            best[r["investigation_id"]] = r
        else:
            others.setdefault(r["investigation_id"], []).append(r["config_id"])
    inv_rank = list(best.values())  # already sorted by score
    tie = cfg["selection"]["tie_points"]
    for i in range(len(inv_rank) - 1):  # near-ties: stronger evidence first
        a, b = inv_rank[i], inv_rank[i + 1]
        if a["score"] - b["score"] <= tie and (b["evidence"], b["has_1g_comparison"]) > (a["evidence"], a["has_1g_comparison"]):
            inv_rank[i], inv_rank[i + 1] = dict(b, tie_note="within tie margin; ordered by evidence quality"), a
    k = top_k or cfg["selection"]["top_k"]
    conf = cfg["confidence"]
    picked = inv_rank[:k]
    cs = cfg.get("complementary_slot") or {}
    d = cs.get("dimension")
    unusual = sc.get("o2_pct") is not None and abs(sc["o2_pct"] - cs.get("only_if_o2_differs_from_pct", -999)) > cs.get("tolerance_pct", 0)
    if cs.get("enabled") and d and unusual and d in scored[0]["similarity"] and len(picked) == k and picked:
        def covers(r):
            return d not in r["unknown_dims"] and r["similarity"].get(d, 0) >= cs["min_similarity"] \
                and not (d == "o2" and "O2" in r.get("assumed_dims", []))
        if not any(covers(r) for r in picked):
            keep = {r["investigation_id"] for r in picked[:-1]}
            cands = [r for r in scored if covers(r) and r["investigation_id"] not in keep
                     and r["score"] >= cs["min_score_ratio"] * picked[0]["score"]]
            if cands:
                comp = dict(cands[0], complementary=d)
                comp["warnings"] = comp["warnings"] + [{"code": "complementary", "message": W["complementary"]}]
                comp["other_configs"] = []
                picked = picked[:-1] + [comp]
    results = []
    for n, r in enumerate(picked, start=1):
        r = dict(r, rank=n)
        r.setdefault("other_configs", others.get(r["investigation_id"], []))
        if not r.get("complementary"):
            r["other_configs"] = others.get(r["investigation_id"], [])
        r["confidence"] = "high" if r["coverage"] >= conf["high"] else "medium" if r["coverage"] >= conf["medium"] else "low"
        results.append(r)
    if sc.get("fuel_phase") == "solid" and results and all((x["gate"] < 1 or "gas_for_solid" in [w["code"] for w in x["warnings"]]) for x in results):
        warnings.append({"code": "weak_match", "message": "No close solid-material match; treat the ranking as indicative."})
    return dict(base, status="ok", profile=profile, weights=weights, warnings=warnings,
                results=results, ranking=inv_rank)


# ----------------------------------------------------------------------------------- CLI
def _print(out):
    print(f"status: {out['status']}  profile: {out.get('profile', '-')}")
    print("scenario:", json.dumps(out["scenario"], ensure_ascii=False))
    for a in out["assumptions"]:
        print(f"  assumed {a['field']} = {a['value']} ({a['source']})")
    for w in out["warnings"]:
        print(f"  ! {w['code']}: {w['message']}")
    for r in out["results"]:
        print(f"#{r['rank']} {r['investigation_id']:<22} {r['score']:5.1f}  [{r['config_id']}] conf={r['confidence']}")
        print(f"     why: {r['why']}")
        if r["main_gap"]:
            print(f"     gap: {r['main_gap']}")
        for w in r["warnings"]:
            print(f"     - {w['code']}: {w['message']}")


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    q = args[0]
    try:
        q = json.loads(q)
    except ValueError:
        pass
    out = rank(q)
    if as_json:
        out = {k: v for k, v in out.items() if k != "ranking"}
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        _print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
