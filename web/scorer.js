// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14).
//
// JavaScript port of scoring/scorer.py (rank, interpret and helpers), for the static
// dashboard. It reads the same scoring/scoring_config.json and data/catalog/*.csv.
// web/parity_check.py runs both implementations on the validation scenarios and more
// queries; the deploy fails if they disagree. Change scorer.py first, then mirror here.
// Scores are the team's computation, not NASA's conclusion.

// ------------------------------------------------------------------------------ helpers
const UNITS_TO_KPA = { kpa: 1.0, psi: 6.89476, psia: 6.89476, atm: 101.325, bar: 100.0, mmhg: 0.133322 };
const NUM_RE = /^\s*[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\s*$/;

function f(v) { // Python float(v) or None
  if (v === null || v === undefined) return null;
  if (typeof v === "number") return v;
  return NUM_RE.test(String(v)) ? Number(v) : null;
}
function split(v) {
  return String(v || "").split(/[;,]/).map((p) => p.trim().toLowerCase()).filter((p) => p);
}
function pyRound(x, n) { // mirrors _r() in scoring/scorer.py: snap to 9 decimals, then half up
  const m = 10 ** n;
  return Math.floor(Number(x.toFixed(9)) * m + 0.5) / m;
}
function fmtG(x) { return String(parseFloat(Number(x).toPrecision(6))); }
function get(obj, key, dflt) { return Object.prototype.hasOwnProperty.call(obj, key) ? obj[key] : dflt; }
function cmp(a, b) { return a < b ? -1 : a > b ? 1 : 0; }
function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\\/-]/g, "\\$&"); }

export function parseCSV(text) {
  const rows = [];
  let row = [], field = "", i = 0, inQ = false;
  if (text.charCodeAt(0) === 0xfeff) i = 1;
  for (; i < text.length; i++) {
    const ch = text[i];
    if (inQ) {
      if (ch === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; } else inQ = false;
      } else field += ch;
    } else if (ch === '"') inQ = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(field); rows.push(row); row = []; field = "";
    } else field += ch;
  }
  if (field !== "" || row.length) { row.push(field); rows.push(row); }
  const hdr = rows.shift() || [];
  return rows.filter((r) => r.length > 1 || r[0] !== "").map((r) => {
    const o = {};
    hdr.forEach((h, j) => { o[h] = r[j] === undefined ? "" : r[j]; });
    return o;
  });
}

// ------------------------------------------------------------------------ interpretation
function has(text, key) {
  key = key.toLowerCase();
  const k = key.trim();
  if (/^[a-z0-9 \-/+.]+$/.test(k)) {
    return new RegExp("(?<![a-z0-9])" + escapeRe(k) + "(?![a-z0-9])").test(text);
  }
  if ([...k].length === 1) {
    return text.trim().split(/\s+/).some((t) => t.startsWith(k) && [...t].length <= 3);
  }
  return text.includes(key);
}
function any(text, keys) { return keys.some((k) => has(text, k)); }
function spans(text, key) { // mirrors _spans: where key matches, by the same rules as has()
  key = key.toLowerCase();
  const k = key.trim();
  const out = [];
  if (/^[a-z0-9 \-/+.]+$/.test(k)) {
    const re = new RegExp("(?<![a-z0-9])" + escapeRe(k) + "(?![a-z0-9])", "g");
    for (const m of text.matchAll(re)) out.push([m.index, m.index + m[0].length]);
    return out;
  }
  if ([...k].length === 1) {
    for (const m of text.matchAll(/\S+/g)) if (m[0].startsWith(k) && [...m[0]].length <= 3) out.push([m.index, m.index + m[0].length]);
    return out;
  }
  let i = text.indexOf(key);
  while (i >= 0) { out.push([i, i + key.length]); i = text.indexOf(key, i + 1); }
  return out;
}
// Korean input words in the patterns: 산소 = oxygen, 농도 = concentration.
const NUMBER_PATTERNS = [/(\d+(?:\.\d+)?)\s*%\s*(?:o2|oxygen|산소)(?![a-z0-9])/g,
  /(?<![a-z0-9])(?:o2|oxygen|산소)\s*(?:농도)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?/g,
  /(\d+(?:\.\d+)?)\s*(kpa|psia|psi|atm|bar|mmhg)(?![a-z])/g, /(\d+(?:\.\d+)?)\s*(cm\/s|mm\/s|m\/s)/g];
export function notUnderstood(query, cfg) { // mirrors not_understood in scorer.py
  const text = String((query && typeof query === "object" ? query.text : query) || "");
  const t = " " + text.toLowerCase().trim() + " ";
  const kw = cfg.keywords;
  let keys = Object.values(cfg.presets).flatMap((p) => p.aliases.concat(p.weak_aliases || []));
  for (const g of ["gravity", "flow_state", "concern", "diluent", "signature"]) keys = keys.concat(Object.values(kw[g] || {}).flat());
  keys = keys.concat(kw.materials.flatMap((m) => m.keys));
  for (const g of ["thin", "thick", "rod", "out_of_scope", "generic"]) keys = keys.concat(kw[g] || []);
  const covered = keys.flatMap((k) => spans(t, k));
  for (const p of NUMBER_PATTERNS) for (const m of t.matchAll(p)) covered.push([m.index, m.index + m[0].length]);
  const phrases = [];
  let cur = [];
  for (const m of t.matchAll(/\S+/g)) {
    const word = m[0].replace(/^[,.;:!?()"']+|[,.;:!?()"']+$/g, "");
    const end = m.index + m[0].length;
    if (!word || covered.some(([a, b]) => a < end && m.index < b)) {
      if (cur.length) { phrases.push(cur.join(" ")); cur = []; }
      continue;
    }
    cur.push(word);
  }
  if (cur.length) phrases.push(cur.join(" "));
  return phrases;
}
function signatureOf(t, keys) { // mirrors _signature: "gas", "particulate", "gas_and_particulate" or null
  t = t.replace(/(?<![a-z0-9])co-(?=[a-z])/g, "co"); // "co-flow" is not carbon monoxide
  const found = ["gas", "particulate"].filter((g) => any(t, keys[g] || []));
  return found.length === 2 ? "gas_and_particulate" : found.length ? found[0] : null;
}
function matchMaterial(t, materials) {
  for (const m of materials) if (any(t, m.keys)) return m;
  return null;
}

export function interpret(query, cfg) {
  let q = {}, text;
  if (query && typeof query === "object") {
    q = { ...query };
    text = String(q.text || "");
    delete q.text;
  } else text = String(query || "");
  const t = " " + text.toLowerCase().trim() + " ";
  const kw = cfg.keywords;
  const sc = {}, src = {};
  const put = (field, value, source) => {
    if (value === null || value === undefined || value === "") return;
    sc[field] = value;
    src[field] = source;
  };
  let preset = q.preset;
  if (!preset) {
    for (const [name, p] of Object.entries(cfg.presets)) {
      if (any(t, p.aliases)) { preset = name; break; }
    }
    if (!preset) { // weak aliases ("spacecraft") count only when no preset is named (mirrors scorer.py)
      for (const [name, p] of Object.entries(cfg.presets)) {
        if (any(t, p.weak_aliases || [])) { preset = name; break; }
      }
    }
  }
  if (preset) {
    if (!(preset in cfg.presets)) throw new Error("unknown preset: " + preset);
    for (const [k, v] of Object.entries(cfg.presets[preset].values)) put(k, v, "preset:" + preset);
    sc.preset = preset;
  }
  for (const [g, keys] of Object.entries(kw.gravity)) if (any(t, keys)) { put("gravity", g, "text"); break; }
  for (const st of ["quiescent", "opposed", "concurrent", "ventilated"]) if (any(t, kw.flow_state[st])) { put("flow_state", st, "text"); break; }
  for (const c of ["detection", "suppression", "prevention"]) if (any(t, kw.concern[c])) { put("concern", c, "text"); break; }
  for (const [dil, keys] of Object.entries(kw.diluent)) if (any(t, keys)) { put("diluent", dil, "text"); break; }
  let mat = matchMaterial(t, kw.materials);
  if (mat) for (const [k, v] of Object.entries(mat)) if (k !== "keys") put(k, v, "text");
  if (any(t, kw.thin)) put("thermal_regime", "thin", "text");
  else if (any(t, kw.thick)) put("thermal_regime", "thick", "text");
  if (any(t, kw.rod)) put("sample_geometry", "rod", "text");
  // "o2" must stand alone: "CO2 30%" is not 30% oxygen (mirrors scorer.py); 산소 = oxygen, 농도 = concentration
  let m = t.match(/(\d+(?:\.\d+)?)\s*%\s*(?:o2|oxygen|산소)(?![a-z0-9])/) ||
    t.match(/(?<![a-z0-9])(?:o2|oxygen|산소)\s*(?:농도)?\s*[:=]?\s*(\d+(?:\.\d+)?)\s*%?/);
  if (m) put("o2_pct", parseFloat(m[1]), "text");
  m = t.match(/(\d+(?:\.\d+)?)\s*(kpa|psia|psi|atm|bar|mmhg)(?![a-z])/);
  if (m) put("pressure_kpa", pyRound(parseFloat(m[1]) * UNITS_TO_KPA[m[2]], 1), "text");
  m = t.match(/(\d+(?:\.\d+)?)\s*(cm\/s|mm\/s|m\/s)/);
  if (m) put("flow_cms", parseFloat(m[1]) * { "cm/s": 1.0, "mm/s": 0.1, "m/s": 100.0 }[m[2]], "text");
  const outOfScope = any(t, kw.out_of_scope);

  if (q.fuel) {
    mat = matchMaterial(" " + String(q.fuel).toLowerCase() + " ", kw.materials);
    if (mat) { for (const [k, v] of Object.entries(mat)) if (k !== "keys") put(k, v, "input"); }
    else put("fuel_material", String(q.fuel).toLowerCase(), "input");
  }
  for (const k of ["o2_pct", "pressure_kpa", "flow_cms"]) if (q[k] !== undefined && q[k] !== null) put(k, Number(q[k]), "input");
  for (const k of ["flow_state", "fuel_phase", "fuel_class", "fuel_material", "melt_behavior", "thermal_regime",
    "sample_geometry", "concern", "diluent", "gravity"]) if (q[k]) put(k, q[k], "input");
  if (!("flow_state" in sc) && sc.flow_cms !== undefined && sc.flow_cms !== null) put("flow_state", sc.flow_cms === 0 ? "quiescent" : "ventilated", "derived");
  if (sc.flow_state === "quiescent" && !("flow_cms" in sc)) put("flow_cms", 0.0, "derived");
  if (!("concern" in sc)) put("concern", cfg.default_profile, "default");
  if (q.profile) put("concern", q.profile, "input");
  if (sc.concern === "detection") { // fire signature of a detection question (similarity.role.signatures)
    if (q.signature) put("signature", q.signature, "input");
    else put("signature", signatureOf(t, kw.signature || {}), "text");
    // In a detection question a carbon dioxide word names a fire signature, not a diluent (scored for suppression only).
    if ((sc.signature === "gas" || sc.signature === "gas_and_particulate") && src.diluent === "text" && sc.diluent === "CO2") {
      delete sc.diluent; delete src.diluent;
    }
  }

  const assumptions = Object.entries(src).filter(([, s]) => s.startsWith("preset") || s === "default" || s === "derived")
    .map(([k, s]) => ({ field: k, value: sc[k], source: s }));
  let informative = Object.keys(sc).filter((k) => k !== "preset" && (src[k] === "text" || src[k] === "input"));
  if (!informative.length) informative = Object.keys(sc).filter((k) => (src[k] || "").startsWith("preset"));
  return { sc, src, assumptions, outOfScope, informative };
}

// --------------------------------------------------------------------------- similarity
function range(c, lo, hi) {
  const a = f(c[lo]), b = f(c[hi]);
  if (a === null && b === null) return null;
  return [a !== null ? a : b, b !== null ? b : a];
}
function sO2(x, c, p) {
  // An inverse flame's O2 is the burner's oxidizer stream; the surrounding atmosphere is fuel and
  // inert gas. It is not an atmosphere a crew breathes, so it is never matched with the user's O2.
  if ((c.o2_reference || "") === "oxidizer_stream") return null;
  const r = range(c, "o2_min_pct", "o2_max_pct");
  if (!r) return null;
  const [lo, hi] = r;
  if (lo <= x && x <= hi) return 1.0;
  // Distance on the log of the O2 ratio (mirrors s_o2; scoring/MODEL_BASIS.md).
  if (x > hi) return Math.exp(-Math.log(x / hi) / p.above_scale_ln);
  if (x <= 0) return 0.0;
  return Math.exp(-Math.log(lo / x) / p.below_scale_ln);
}
function logGauss(x, lo, hi, sigma, offset = 0.0) {
  if (lo <= x && x <= hi) return 1.0;
  const near = x < lo ? lo : hi;
  const z = Math.log((x + offset) / (near + offset)) / sigma;
  return Math.exp(-0.5 * z * z);
}
function sPressure(x, c, p) {
  const r = range(c, "pressure_min_kpa", "pressure_max_kpa");
  return r ? logGauss(x, r[0], r[1], p.sigma_ln) : null;
}
function speedSim(v, c, sim) { // mirrors _speed: [similarity, in-range signal for outside_range]
  // With one end not recorded ("up to 40 cm/s", a limit, not a test value), a speed on the open side scores
  // unknown_value and raises no warning; beyond the end it decays from unknown_value, with no jump.
  const a = f(c.flow_min_cms), b = f(c.flow_max_cms);
  if (a === null && b === null) return [null, null];
  const p = sim.flow_speed;
  if (a === null || b === null) {
    const end = a === null ? b : a;
    if ((a === null && v <= end) || (b === null && v >= end)) return [sim.unknown_value, null];
    const g = logGauss(v, end, end, p.sigma_ln, p.offset_cms);
    return [sim.unknown_value * g, g];
  }
  const s = logGauss(v, a, b, p.sigma_ln, p.offset_cms);
  return [s, s];
}
function sFlow(state, v, c, sim) {
  const cfgs = split(c.flow_config);
  let sCfg = null;
  if (state && cfgs.length) {
    const row = sim.flow_config_matrix[state];
    sCfg = Math.max(...cfgs.map((k) => get(row, k, 0.3)));
  }
  const sV = v !== null && v !== undefined ? speedSim(v, c, sim)[0] : null;
  const parts = [sCfg, sV].filter((x) => x !== null);
  if (!parts.length) return null;
  return parts.length === 2 ? parts[0] * parts[1] : parts[0];
}
function sFuel(sc, c, p) {
  const phase = sc.fuel_phase, cls = sc.fuel_class, mat = sc.fuel_material, melt = sc.melt_behavior;
  const cphase = (c.fuel_phase || "").toLowerCase();
  if (!cphase) return null;
  if (mat && (c.fuel_material || "").toLowerCase().includes(String(mat).toLowerCase())) return p.same_material;
  if (cls && split(c.fuel_class).includes(cls)) {
    const cmelt = (c.melt_behavior || "").toLowerCase();
    if (melt && cmelt && melt === cmelt) return p.same_class_same_melt;
    return p.same_class;
  }
  if (phase && phase === cphase) return p.same_phase;
  if (phase === "solid" && (c.surrogate_for || "").toLowerCase() === "solid") return p.solid_surrogate;
  if (phase && new Set([phase, cphase]).size === 2 && [phase, cphase].includes("liquid") && [phase, cphase].includes("gas")) return p.liquid_gas;
  return p.other;
}
function sGeometry(sc, c, p) {
  const ug = sc.sample_geometry, ur = sc.thermal_regime;
  const cg = split(c.sample_geometry), cr = split(c.thermal_regime);
  if (!cg.length) return null;
  const solid = new Set(p.solid_geometries);
  const userSolid = sc.fuel_phase === "solid" || solid.has(ug) || (ur !== undefined && ur !== null);
  const cfgSolid = cg.some((g) => solid.has(g));
  if ((userSolid && !cfgSolid) || (ug && !userSolid && cfgSolid)) return p.phase_family_mismatch;
  const sameG = ug ? cg.includes(ug) : null;
  const sameR = ur && cr.length ? cr.includes(ur) : null;
  if (sameG && sameR !== false) return p.same_geometry;
  if (sameG && sameR === false) return p.same_geometry_other_regime;
  if (sameR) return p.other_geometry_same_regime;
  if (sameG === null && sameR === null) return null;
  return p.solid_other;
}
function roleMatch(concern, c, p, signature = null) { // mirrors role_match: [similarity, note]
  const inv = c._inv;
  const roles = split(inv.fire_safety_role), focus = split(inv.research_focus);
  const sg = p.signatures;
  if (concern === "detection" && sg) {
    const sigs = signature === "gas" || signature === "particulate" ? [signature] : ["gas", "particulate"];
    const stated = get(sg.stated_purpose || {}, c.investigation_id, null);
    const byLabel = roles.includes("detection");
    const byStatement = !!stated && sigs.includes(stated.signature);
    const outs = new Set(split(c.measured_outputs).map((x) => x.replace(/\s*\(.*\)$/, "")));
    const notFire = Object.prototype.hasOwnProperty.call(sg.not_from_a_fire || {}, c.investigation_id);
    const measured = notFire ? [] // particles of a dust standard, not of a fire
      : sigs.filter((g) => (sg.outputs[g] || []).some((x) => outs.has(x)) || focus.some((x) => (sg.focus[g] || []).includes(x)));
    const purpose = byLabel ? "detection label" : byStatement ? `NASA-stated ${stated.signature} measurement purpose` : "";
    const outcome = notFire ? "measured particles not produced by a fire" : measured.length ? `measured ${measured.join(" and ")} signature` : "";
    const note = [purpose, outcome].filter((x) => x).join("; ") || "no detection purpose or signature measurement";
    if (purpose && measured.length) return [p.same_axis, note];
    if (purpose || measured.length) return [p.related_focus, note];
    return [roles.includes("fundamental") ? p.fundamental : p.other, note];
  }
  if (roles.includes(concern)) return [p.same_axis, ""];
  const rel = get(p.related_focus_by_axis, concern, []);
  if (focus.some((x) => rel.includes(x))) return [p.related_focus, ""];
  if (roles.includes("fundamental")) return [p.fundamental, ""];
  return [p.other, ""];
}
function sRole(concern, c, p, signature = null) { return roleMatch(concern, c, p, signature)[0]; }
function sDiluent(dil, c, p) {
  const cd = split(c.diluent);
  if (!cd.length) return p.none;
  const d = String(dil).toLowerCase();
  if (cd.includes(d)) return p.same;
  // Another inert: compared by molar heat capacity (mirrors s_diluent).
  const cp = {};
  for (const [k, v] of Object.entries(p.molar_cp_298K_kJ_per_kmolK || {})) cp[k.toLowerCase()] = v;
  const u = get(cp, d, null);
  const k = get(p, "cp_ratio_exponent", 1);
  const vals = u === null ? [] : cd.filter((x) => x in cp).map((x) => Math.pow(Math.min(u, cp[x]) / Math.max(u, cp[x]), k));
  return vals.length ? Math.max(...vals) : p.other_inert;
}
function evidence(c, e) {
  const inv = c._inv;
  const q = [get(e.data_availability, inv.data_availability, 0.5),
    get(e.mu_g_duration_class, inv.mu_g_duration_class, 0.5),
    get(e.verification_status, inv.verification_status, 0.7)];
  return e.base + e.span * (q[0] + q[1] + q[2]) / 3;
}

// ------------------------------------------------------------------------------ ranking
function withFallback(c, cfg) {
  const fb = cfg.atmosphere_fallback || {};
  const c2 = { ...c }, used = [];
  if (fb.o2_pct !== undefined && fb.o2_pct !== null && !range(c, "o2_min_pct", "o2_max_pct") &&
      (fb.o2_applies_to === "all" || (fb.o2_applies_to || []).includes(c.investigation_id))) {
    c2.o2_min_pct = c2.o2_max_pct = fb.o2_pct;
    used.push("O2");
  }
  if (fb.pressure_kpa !== undefined && fb.pressure_kpa !== null && !range(c, "pressure_min_kpa", "pressure_max_kpa") &&
      (fb.pressure_applies_to_investigations || []).includes(c.investigation_id)) {
    c2.pressure_min_kpa = c2.pressure_max_kpa = fb.pressure_kpa;
    if (Object.prototype.hasOwnProperty.call(fb.pressure_published || {}, c.investigation_id)) c2.pressure_source = "published"; // documented, not assumed
    else used.push("pressure");
  }
  return [c2, used];
}
function similarities(sc, c, cfg) {
  const sim = cfg.similarity;
  const [ce, fallback] = withFallback(c, cfg);
  const S = {};
  let speed = null;
  if (sc.o2_pct !== undefined && sc.o2_pct !== null) S.o2 = sO2(sc.o2_pct, ce, sim.o2);
  if (sc.pressure_kpa !== undefined && sc.pressure_kpa !== null) S.pressure = sPressure(sc.pressure_kpa, ce, sim.pressure);
  const hasV = sc.flow_cms !== undefined && sc.flow_cms !== null;
  if (sc.flow_state || hasV) {
    S.flow = sFlow(sc.flow_state, hasV ? sc.flow_cms : null, ce, sim);
    if (hasV) speed = speedSim(sc.flow_cms, ce, sim)[1];
  }
  if (sc.fuel_phase || sc.fuel_class || sc.fuel_material) S.fuel = sFuel(sc, ce, sim.fuel);
  if (sc.sample_geometry || sc.thermal_regime) S.geometry = sGeometry(sc, ce, sim.geometry);
  S.role = sRole(sc.concern, ce, sim.role, get(sc, "signature", null));
  if (sc.concern === "suppression" && sc.diluent) S.diluent = sDiluent(sc.diluent, ce, sim.diluent);
  return [S, fallback, speed, ce];
}
function scoreConfig(sc, c, cfg, weights, rawS, caps, assumed = []) { // assumed: dims whose value no NASA source states
  const sim = cfg.similarity;
  const S = {}, unknown = [];
  for (const [d, v] of Object.entries(rawS)) {
    if (v === null) { unknown.push(d); S[d] = Math.min(sim.unknown_value, get(caps, d, 1.0)); }
    else S[d] = v;
  }
  let w = {};
  for (const d of Object.keys(S)) { const x = get(weights, d, 0.0); if (x > 0) w[d] = x; }
  const tot = Object.values(w).reduce((a, b) => a + b, 0) || 1.0;
  const wn = {};
  for (const [d, x] of Object.entries(w)) wn[d] = x / tot;
  w = wn;
  let raw = 0;
  for (const d of Object.keys(w)) raw += w[d] * S[d];
  let gate = 1.0;
  const g = cfg.gate;
  for (const d of g.dimensions) {
    if (d in S && S[d] < g.min_similarity) {
      gate = g.mode === "ramp" ? Math.min(gate, g.factor + (1 - g.factor) * S[d] / g.min_similarity) : Math.min(gate, g.factor);
    }
  }
  const M = evidence(c, cfg.evidence);
  const score = 100.0 * M * gate * raw;
  let full = 0;
  for (const [k, v] of Object.entries(weights)) if (v > 0 && (k !== "diluent" || sc.concern === "suppression")) full += v;
  let knownW = 0;
  // Confidence counts only what was compared with a value a NASA source states (mirrors score_config).
  for (const d of Object.keys(w)) if (!unknown.includes(d) && !assumed.includes(d)) knownW += weights[d];
  const coverage = full ? knownW / full : 0.0;
  const contributions = {};
  for (const d of Object.keys(w)) contributions[d] = w[d] * S[d];
  return { score, raw, gate, evidence: M, similarity: S, weights: w, unknown, coverage, contributions };
}
function fmtRange(c, lo, hi, unit) {
  // Text only (mirrors _fmt_range). When one end is not recorded, say so ("up to 40 cm/s" in the
  // PSI-26 record is not "at 40 cm/s"). Similarity still uses range(), which treats the recorded end as both ends.
  const a = f(c[lo]), b = f(c[hi]);
  if (a === null && b === null) return "not reported";
  if (a === null) return `up to ${fmtG(b)}${unit}`;
  if (b === null) return `at least ${fmtG(a)}${unit}`;
  return a === b ? `${fmtG(a)}${unit}` : `${fmtG(a)}–${fmtG(b)}${unit}`;
}
// How a number is worded by where it comes from (mirrors SOURCE_NOTE in scorer.py).
const SOURCE_NOTE = { record: "named in the PSI record, not a test value", test_matrix: "from the test matrix, not individual tests",
  team: "team reading, not in the table", published: "stated in a published paper, not a test value" };
const NOT_RECORDED = ["assumed", "team"]; // bases with no NASA source for the value (mirrors scorer.py)
function valueBasis(sc, c, S, fallback) { // mirrors value_basis
  const out = {};
  for (const [d, v] of Object.entries(S)) {
    if (v === null) out[d] = "none";
    else if (d === "o2" || d === "pressure") out[d] = fallback.includes(d === "o2" ? "O2" : "pressure") ? "assumed" : (c[`${d}_source`] || "none");
    else if (d === "flow" && sc.flow_cms !== undefined && sc.flow_cms !== null && range(c, "flow_min_cms", "flow_max_cms")) out[d] = c.flow_source || "table";
    else out[d] = "catalog";
  }
  return out;
}
function fmtValue(c, v, label, lo, hi, unit, assumed) { // mirrors _fmt_value
  const r = fmtRange(c, lo, hi, unit);
  if (assumed) return `${label} not recorded, assumed ${r}`;
  const note = get(SOURCE_NOTE, c[`${v}_source`] || "", null);
  return note ? `${label} ${r}, ${note}` : `${label} tested ${r}`;
}
function fmtFlow(c) { // mirrors _fmt_flow
  const r = fmtRange(c, "flow_min_cms", "flow_max_cms", " cm/s");
  const head = `flow ${c.flow_config || "n/a"}`;
  if (r === "not reported") return `${head}, speed not reported`;
  const text = r.startsWith("up to") || r.startsWith("at least") ? `${head}, ${r}` : `${head} at ${r}`;
  const note = get(SOURCE_NOTE, c.flow_source || "", null);
  return note ? `${text}, ${note}` : text;
}
function fill(tpl, vars) { return tpl.replace(/\{(\w+)\}/g, (_, k) => vars[k]); }
function explain(sc, c, s, cfg, fallback, speed, unrecorded = null) {
  const sim = s.similarity, W = cfg.warnings;
  const labels = { o2: "O2", pressure: "pressure", flow: "flow", fuel: "fuel", geometry: "sample shape", role: "research purpose", diluent: "diluent" };
  const known = Object.keys(s.contributions).filter((d) => !s.unknown.includes(d));
  const fb = fallback || [];
  const assumed = unrecorded ? new Set(unrecorded) : new Set([...(fb.includes("O2") ? ["o2"] : []), ...(fb.includes("pressure") ? ["pressure"] : [])]);
  // Reasons come from recorded values first; an assumed (not recorded) value is a reason only if nothing else is left.
  const best = [...known].sort((a, b) => (assumed.has(a) - assumed.has(b)) || (-s.contributions[a] - -s.contributions[b])).slice(0, 2);
  const gaps = [...known].sort((a, b) => sim[a] - sim[b]).slice(0, 1);
  const detail = {
    // "tested" only for numbers from an experimental table; assumed, record and matrix values say so.
    o2: fmtValue(c, "o2", "O2", "o2_min_pct", "o2_max_pct", "%", fb.includes("O2")),
    pressure: fmtValue(c, "pressure", "pressure", "pressure_min_kpa", "pressure_max_kpa", " kPa", fb.includes("pressure")),
    flow: fmtFlow(c),
    fuel: `fuel ${c.fuel_material}`,
    geometry: `${c.sample_geometry} (${c.thermal_regime || "regime n/a"})`,
    role: [`role ${c._inv.fire_safety_role}`, roleMatch(sc.concern, c, cfg.similarity.role, get(sc, "signature", null))[1]].filter((x) => x).join("; "),
    diluent: `diluent ${c.diluent || "none"}`,
  };
  const why = best.map((d) => `${labels[d]} match ${sim[d].toFixed(2)} (${detail[d]})`).join("; ");
  const gap = gaps.filter((d) => sim[d] < 0.9).map((d) => `${labels[d]} ${sim[d].toFixed(2)} (${detail[d]})`).join("; ");
  const warns = [];
  const stream = (c.o2_reference || "") === "oxidizer_stream";
  const o2max = stream ? null : f(c.o2_max_pct);
  if (sc.o2_pct !== undefined && sc.o2_pct !== null && o2max !== null && sc.o2_pct > o2max) {
    warns.push({ code: "o2_above_result", message: fill(W.o2_above_result, { user: fmtG(sc.o2_pct), max: fmtG(o2max) }) });
  }
  const thr = get(cfg, "outside_range_threshold", 0.9);
  const out = known.filter((d) => (d === "o2" || d === "pressure") && sim[d] < thr).map((d) => labels[d]);
  if (speed !== null && speed < thr) out.push("flow speed");
  if (out.length) warns.push({ code: "outside_range", message: fill(W.outside_range, { dims: out.join(", ") }) });
  // pm decision 14:15: two true ranges compared side by side must not read as one test at both values.
  const isSpan = (lo, hi) => { const a = f(c[lo]), b = f(c[hi]); return a !== null && b !== null && a < b; };
  if (known.includes("o2") && known.includes("pressure") && !fb.includes("O2") && !fb.includes("pressure") &&
      isSpan("o2_min_pct", "o2_max_pct") && isSpan("pressure_min_kpa", "pressure_max_kpa")) {
    warns.push({ code: "ranges_separate", message: W.ranges_separate });
  }
  if (sc.fuel_phase === "solid" && (c.fuel_phase || "").toLowerCase() === "gas") warns.push({ code: "gas_for_solid", message: W.gas_for_solid });
  if (stream && "o2" in sim) warns.push({ code: "oxidizer_stream", message: W.oxidizer_stream });
  const missing = s.unknown.filter((d) => !(stream && d === "o2")); // O2 of a stream is recorded, just not comparable
  if (missing.length) warns.push({ code: "not_reported", message: fill(W.not_reported, { dims: missing.map((d) => labels[d]).join(", ") }) });
  if (fallback.length) warns.push({ code: "fallback", message: fill(W.fallback, { dims: fallback.join(" and ") }) });
  if (c._inv.platform === "ground") warns.push({ code: "ground_analysis", message: W.ground_analysis });
  return [why, gap, warns];
}
function roundMap(m, n) { const o = {}; for (const [k, v] of Object.entries(m)) o[k] = pyRound(v, n); return o; }

// ---------------------------------------------------------------- requirements (mirrors scorer.py)
const SOURCE_RANK = ["stated", "implied", "derived", "assumed"];
function reqSource(s, classes) {
  if (s.startsWith("preset:")) return ["implied", "implied by preset " + s.split(":").slice(1).join(":")];
  const k = get(classes, s, "assumed");
  return [k, k];
}
export function requirements(sc, src, cfg) {
  const spec = cfg.requirements || {};
  const classes = spec.source_class || {};
  const out = [];
  for (const g of spec.groups || []) {
    const present = g.fields.filter((fld) => sc[fld] !== undefined && sc[fld] !== null && sc[fld] !== "");
    if (!present.length) continue;
    const units = g.units || {};
    const vals = present.map((fld) => (typeof sc[fld] === "number" ? fmtG(sc[fld]) + get(units, fld, "") : String(sc[fld])));
    const cls = present.map((fld) => reqSource(get(src, fld, ""), classes));
    let best = 0;
    for (let i = 1; i < cls.length; i++) if (SOURCE_RANK.indexOf(cls[i][0]) < SOURCE_RANK.indexOf(cls[best][0])) best = i;
    out.push({ id: `R${out.length + 1}`, dimension: g.dimension, kind: g.kind, label: g.label, value: vals.join(", "),
      source_class: cls[best][0], source: cls[best][1], verified_by: g.verified_by });
  }
  return out;
}
function compliance(reqs, r, sc, cfg) { // mirrors compliance: status and the basis of the value checked
  const thr = get(cfg, "outside_range_threshold", 0.9);
  const assumed = new Set((r.assumed_dims || []).map((x) => ({ O2: "o2", pressure: "pressure" })[x] || x));
  const basis = r.value_basis || {};
  return reqs.map((q) => {
    const d = q.dimension;
    let st, b = "";
    if (d === "gravity") {
      const g = sc.gravity;
      b = "catalog";
      st = g === "microgravity" ? "met" : g === "earth" && r.has_1g_comparison ? "near" : "not_met";
    } else if (!(d in r.similarity)) st = "not_scored";
    else {
      b = r.unknown_dims.includes(d) ? "none" : assumed.has(d) ? "assumed" : get(basis, d, "catalog");
      if (b === "none" || NOT_RECORDED.includes(b)) st = "unverified";
      else {
        const v = r.similarity[d];
        st = v >= 0.999 ? (b === "table" || b === "catalog" ? "met" : "documented") : v >= thr ? "near" : "not_met";
      }
    }
    return { id: q.id, status: st, basis: b };
  });
}

const TIE_NOTE = "within the tie margin of the best remaining score; ordered by recorded share, then evidence";
function orderTies(rows, tie) { // mirrors order_ties: at each place, the near-tie group by coverage, evidence, score
  const rest = [...rows], out = [];
  while (rest.length) {
    const top = rest[0].score;
    const group = rest.filter((r) => pyRound(top - r.score, 6) <= tie);
    group.sort((a, b) => (b.coverage - a.coverage) || (b.evidence - a.evidence) || (b.score - a.score) || cmp(a.config_id, b.config_id));
    const pick = group[0];
    rest.splice(rest.indexOf(pick), 1);
    out.push(pick.score < top ? { ...pick, tie_note: TIE_NOTE } : pick);
  }
  return out;
}

export function createScorer({ config, investigationsCsv, configurationsCsv }) {
  const invRows = parseCSV(investigationsCsv);
  const inv = {};
  for (const r of invRows) inv[r.investigation_id] = r;
  const cfgs = parseCSV(configurationsCsv).map((c) => ({ ...c, _inv: inv[c.investigation_id] }));

  function rank(query, { topK = null, weightsOverride = null } = {}) {
    const cfg = config;
    const { sc, src, assumptions, outOfScope, informative } = interpret(query, cfg);
    const W = cfg.warnings;
    const unread = notUnderstood(query, cfg);
    const reqs = requirements(sc, src, cfg);
    const base = { scenario: { ...sc }, sources: src, assumptions, config_version: cfg.version, not_understood: unread, requirements: reqs };
    const unreadW = unread.length ? [{ code: "not_understood", message: fill(W.not_understood, { words: unread.map((p) => `'${p}'`).join(", ") }) }] : [];
    if (outOfScope) return { ...base, status: "out_of_scope", warnings: [{ code: "out_of_scope", message: W.out_of_scope }], results: [], ranking: [] };
    if (!informative.length) return { ...base, status: "need_input", warnings: [{ code: "need_input", message: W.need_input }, ...unreadW], results: [], ranking: [] };
    const profile = sc.concern in cfg.profiles ? sc.concern : cfg.default_profile;
    const weights = { ...cfg.profiles[profile].weights, ...(weightsOverride || {}) };
    const warnings = [...unreadW];
    const g = sc.gravity;
    if (g === "lunar" || g === "martian" || g === "planetary") warnings.push({ code: "partial_gravity", message: W.partial_gravity });
    else if (g === "earth") warnings.push({ code: "earth_gravity", message: W.earth_gravity });
    let maxO2 = null, maxC = null;
    // Highest O2 of any surrounding atmosphere tested (oxidizer streams of inverse flames excluded).
    for (const c of cfgs) {
      if ((c.o2_reference || "") === "oxidizer_stream") continue;
      const v = f(c.o2_max_pct);
      if (v !== null && (maxO2 === null || v > maxO2)) { maxO2 = v; maxC = c; }
    }
    if (sc.o2_pct !== undefined && sc.o2_pct !== null && sc.o2_pct > maxO2) {
      warnings.push({ code: "o2_above_all", message: fill(W.o2_above_all, { max_o2: fmtG(maxO2), max_cfg: maxC.config_id, ref: maxC.o2_reference || "ambient" }) });
    }
    if (sc.preset === "mars_habitat" && (sc.o2_pct === undefined || sc.o2_pct === null)) {
      warnings.push({ code: "mars_atmosphere", message: cfg.presets.mars_habitat.source });
    }
    const pre = cfgs.map((c) => [c, ...similarities(sc, c, cfg)]);
    const caps = {};
    for (const d of cfg.similarity.unknown_cap_dims || []) {
      const known = pre.map(([, S]) => S[d]).filter((v) => v !== undefined && v !== null);
      if (known.length) caps[d] = Math.max(...known);
    }
    const scored = pre.map(([c, S, fallback, speed, ce]) => {
      const basis = valueBasis(sc, ce, S, fallback);
      const unrecorded = Object.keys(basis).filter((d) => NOT_RECORDED.includes(basis[d]));
      const s = scoreConfig(sc, c, cfg, weights, S, caps, unrecorded);
      const [why, gap, warns] = explain(sc, ce, s, cfg, fallback, speed, unrecorded);
      return {
        config_id: c.config_id, investigation_id: c.investigation_id, psi_accession: c.psi_accession,
        config_label: c.config_label, score: pyRound(s.score, 1), raw: pyRound(s.raw, 3), gate: pyRound(s.gate, 3),
        evidence: pyRound(s.evidence, 3), similarity: roundMap(s.similarity, 3), contributions: roundMap(s.contributions, 3),
        weights_used: roundMap(s.weights, 3), unknown_dims: s.unknown, assumed_dims: fallback, value_basis: basis,
        coverage: pyRound(s.coverage, 2), why, main_gap: gap, warnings: warns,
        psi_url: c._inv.psi_url, dataset_doi: c._inv.dataset_doi,
        key_findings: c.key_findings || c._inv.key_findings,
        has_1g_comparison: c._inv.has_1g_comparison === "Y", verification_status: c._inv.verification_status,
      };
    });
    scored.sort((a, b) => (b.score - a.score) || (b.coverage - a.coverage) || (b.evidence - a.evidence) || cmp(a.config_id, b.config_id));
    const best = new Map(), others = {};
    for (const r of scored) {
      if (!best.has(r.investigation_id)) best.set(r.investigation_id, r);
      else (others[r.investigation_id] = others[r.investigation_id] || []).push(r.config_id);
    }
    const invRank = orderTies([...best.values()], cfg.selection.tie_points);
    const k = topK || cfg.selection.top_k;
    const conf = cfg.confidence;
    let picked = invRank.slice(0, k);
    const cs = cfg.complementary_slot || {};
    const d = cs.dimension;
    const unusual = sc.o2_pct !== undefined && sc.o2_pct !== null &&
      Math.abs(sc.o2_pct - get(cs, "only_if_o2_differs_from_pct", -999)) > get(cs, "tolerance_pct", 0);
    if (cs.enabled && d && unusual && scored.length && d in scored[0].similarity && picked.length === k && picked.length) {
      const covers = (r) => !r.unknown_dims.includes(d) && get(r.similarity, d, 0) >= cs.min_similarity &&
        !(d === "o2" && (r.assumed_dims || []).includes("O2"));
      if (!picked.some(covers)) {
        const keep = new Set(picked.slice(0, -1).map((r) => r.investigation_id));
        const cands = scored.filter((r) => covers(r) && !keep.has(r.investigation_id) && r.score >= cs.min_score_ratio * picked[0].score);
        if (cands.length) {
          const comp = { ...cands[0], complementary: d, other_configs: [] };
          comp.warnings = [...comp.warnings, { code: "complementary", message: W.complementary }];
          picked = [...picked.slice(0, -1), comp];
        }
      }
    }
    const results = picked.map((r, n) => {
      const o = { ...r, rank: n + 1 };
      if (!o.complementary) o.other_configs = others[o.investigation_id] || [];
      else if (!o.other_configs) o.other_configs = others[o.investigation_id] || [];
      o.confidence = o.coverage >= conf.high ? "high" : o.coverage >= conf.medium ? "medium" : "low";
      o.compliance = compliance(reqs, o, sc, cfg);
      return o;
    });
    if (sc.fuel_phase === "solid" && results.length && results.every((x) => x.gate < 1 || x.warnings.some((w) => w.code === "gas_for_solid"))) {
      warnings.push({ code: "weak_match", message: "No close solid-material match; treat the ranking as indicative." });
    }
    return { ...base, status: "ok", profile, weights, warnings, results, ranking: invRank };
  }
  return { rank, catalog: { investigations: inv, configurations: cfgs } };
}
