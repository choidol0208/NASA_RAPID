// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14). Dashboard: runs the team's ranking in the
// browser (web/scorer.js, checked against scoring/scorer.py) and renders the result.
import { createScorer, parseCSV } from "./scorer.js";

const REPO_BASE = "https://github.com/choidol0208/NASA_RAPID/blob/";
let REPO = REPO_BASE + "main/"; // replaced by the exact build commit from data/build.json
const DIMS = { o2: "Oxygen", pressure: "Pressure", flow: "Flow", fuel: "Fuel", geometry: "Shape", role: "Purpose", diluent: "Diluent" };
const STOP = new Set(["out_of_scope", "need_input", "o2_above_all", "partial_gravity"]);

const $ = (sel) => document.querySelector(sel);
function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "style") el.setAttribute("style", v);
    else el.setAttribute(k, v);
  }
  for (const kid of kids.flat()) if (kid !== null && kid !== undefined && kid !== false) el.append(kid);
  return el;
}
const link = (href, text) => h("a", { href, target: "_blank", rel: "noopener" }, text);

function cls(v, unknown, assumed) {
  if (unknown) return "s-unk";
  const base = v >= 0.9 ? "s-hi" : v >= 0.5 ? "s-mid" : "s-lo";
  return assumed ? base + " s-asm" : base;
}

function condText(field, value, cfg) {
  const kpaToPsi = (k) => (k / 6.89476).toFixed(1);
  switch (field) {
    case "o2_pct": return ["Oxygen", `${value}%`];
    case "pressure_kpa": return ["Pressure", `${value} kPa (${kpaToPsi(value)} psi)`];
    case "flow_state": return ["Airflow", { quiescent: "still air", ventilated: "ventilated", opposed: "against the flame", concurrent: "with the flame" }[value] || value];
    case "flow_cms": return ["Flow speed", `${value} cm/s`];
    case "fuel_material": return ["Material", value];
    case "fuel_class": return ["Material type", String(value).replace(/_/g, " ")];
    case "fuel_phase": return ["Fuel phase", value];
    case "melt_behavior": return ["Burns by", value === "chars" ? "charring" : value === "melts" ? "melting" : value];
    case "thermal_regime": return ["Thickness", `thermally ${value}`];
    case "sample_geometry": return ["Shape", String(value).replace(/_/g, " ")];
    case "concern": return ["Question", cfg.profiles[value] ? cfg.profiles[value].label_en : value];
    case "gravity": return ["Gravity", value];
    case "diluent": return ["Diluent", value];
    case "preset": return ["Environment", cfg.presets[value] ? cfg.presets[value].label_en : value];
    default: return [field, String(value)];
  }
}
function sourceText(s) {
  if (!s) return "";
  if (s.startsWith("preset:")) return "from the preset";
  return { text: "you", input: "you", default: "default", derived: "derived" }[s] || s;
}

function renderConditions(out, cfg) {
  const ul = $("#conditions");
  ul.replaceChildren();
  const order = ["preset", "o2_pct", "pressure_kpa", "flow_state", "flow_cms", "gravity", "fuel_material", "fuel_class", "fuel_phase", "melt_behavior", "thermal_regime", "sample_geometry", "diluent", "concern"];
  for (const f of order) {
    if (!(f in out.scenario)) continue;
    const [label, val] = condText(f, out.scenario[f], cfg);
    const src = f === "preset" ? "you" : out.sources[f];
    const kind = !src ? "you" : src.startsWith("preset") ? "preset" : src === "default" || src === "derived" ? "default" : "you";
    ul.append(h("li", { class: "from-" + kind }, h("b", {}, label), " ", val, " ", h("span", { class: "src" }, `(${f === "preset" ? "you" : sourceText(src)})`)));
  }
}

function renderAssumptions(out, cfg) {
  const box = $("#assumptions");
  box.replaceChildren();
  const groups = new Map();
  for (const a of out.assumptions || []) {
    const key = a.source || "default";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(a);
  }
  if (!groups.size) return;
  box.append(h("p", { class: "assume-head" }, h("b", {}, "Filled in for you, not typed: "), "type a value to replace any of these."));
  const ul = h("ul", { class: "assume" });
  for (const [src, items] of groups) {
    const vals = items.map((a) => { const [l, v] = condText(a.field, a.value, cfg); return `${l} ${v}`; }).join("; ");
    if (src.startsWith("preset:")) {
      const p = cfg.presets[src.slice(7)];
      ul.append(h("li", {}, vals, ". From the ", h("b", {}, p ? p.label_en : src.slice(7)), " preset. Preset source: ",
        p && p.source ? p.source : "not stated", " ", link(REPO + "scoring/scoring_config.json", "(preset file)")));
    } else {
      ul.append(h("li", {}, vals, ". ", src === "default" ? "Team default when nothing is said." : `Source: ${sourceText(src)}.`, " ",
        link(REPO + "scoring/scoring_config.json", "(config file)")));
    }
  }
  box.append(ul);
}

function renderWarnings(box, warnings) {
  box.replaceChildren();
  for (const w of warnings) box.append(h("p", { class: "warn" + (STOP.has(w.code) ? " is-stop" : "") }, w.message));
}

function strip(r) {
  const dims = Object.keys(r.weights_used);
  const s = h("div", { class: "strip", style: `--n:${dims.length}`, role: "list", "aria-label": "Match by dimension" });
  for (const d of dims) {
    const unknown = r.unknown_dims.includes(d);
    const assumed = (d === "o2" && r.assumed_dims.includes("O2")) || (d === "pressure" && r.assumed_dims.includes("pressure"));
    const v = r.similarity[d];
    s.append(h("div", { class: "cell " + cls(v, unknown, assumed), role: "listitem",
      title: `${DIMS[d]}: ${unknown ? "not reported" : v.toFixed(2)}${assumed ? " (assumed cabin air)" : ""}, weight ${r.weights_used[d].toFixed(2)}` },
      h("span", { class: "dim" }, DIMS[d]), h("span", { class: "val" }, unknown ? "n/r" : v.toFixed(2))));
  }
  return s;
}

function sourceFileLink(ref) {
  if (!ref) return null;
  const file = ref.split(" (")[0].trim();
  if (!file.endsWith(".csv")) return null;
  return link(REPO + "data/psi/experimental_tables/" + encodeURIComponent(file), "Source table");
}


// ------------------------------------------------------------------ model-written text (pm role)
// A source is "PSI-25.objective", "doi:10.x/y" or "data/pipeline/tests.csv#FLEX-12", or an array of them.
function sourceLinks(src, cat) {
  const list = Array.isArray(src) ? src : src ? [src] : [];
  const out = [];
  for (const s0 of list) {
    const s = typeof s0 === "string" ? s0 : s0 && s0.doi ? "doi:" + s0.doi : s0 && s0.investigation_id ? s0.investigation_id + ".record" : "";
    if (!s) continue;
    let a;
    if (s.startsWith("doi:")) a = link("https://doi.org/" + s.slice(4), s.slice(4));
    else if (/^PSI-\d+\./.test(s)) {
      const [acc, field] = [s.slice(0, s.indexOf(".")), s.slice(s.indexOf(".") + 1)];
      a = link(`${REPO}data/psi/catalog/${acc}.json`, `${acc} record, ${field.replace(/_/g, " ")}`);
    } else if (/^PSI-\d+$/.test(s)) a = link(`https://psi.nasa.gov/physci/repo/data/investigations/${s}`, `${s} PSI page`);
    else if (s.includes("#")) { const [f, id] = s.split("#"); a = link(REPO + f, `${f.split("/").pop()}, ${id}`); }
    else a = link(REPO + s, s);
    out.push(a);
  }
  if (!out.length) return h("span", { class: "src-list missing" }, "source not given");
  return h("span", { class: "src-list" }, "(", ...out.flatMap((a, i) => (i ? ["; ", a] : [a])), ")");
}
function aiLabel(x) {
  return h("span", { class: "tag is-ai" }, x && x.reviewed_by ? `AI-generated, reviewed by ${x.reviewed_by}` : "AI-generated, not reviewed yet",
    x && x.model ? `, model ${x.model}` : "");
}
function scenarioNotes(query, out, insights) {
  const q = query.trim().toLowerCase();
  return (insights.scenarios || []).find((e) => typeof e.query === "string" && e.query.trim().toLowerCase() === q && e.id === out.scenario.preset) || null;
}
function noteFor(sc, r) {
  if (!sc || !Array.isArray(sc.result_notes)) return null;
  return sc.result_notes.find((n) => n.investigation_id === r.psi_accession || n.investigation_id === r.investigation_id) || null;
}

function renderResults(out, cat, insights, sc) {
  const ol = $("#results");
  ol.replaceChildren();
  for (const r of out.results) {
    const inv = cat.investigations[r.investigation_id];
    const conf = cat.configurations.find((c) => c.config_id === r.config_id);
    const card = insights.cards[r.psi_accession];
    const head = h("div", { class: "result-head" },
      h("span", { class: "rank", "aria-label": `Rank ${r.rank}` }, String(r.rank)),
      h("h3", {}, `${r.investigation_id}`),
      h("div", { class: "score" }, String(r.score), h("small", {}, "team score")),
      h("p", { class: "subtitle" }, inv ? inv.investigation_name : r.psi_accession));
    const body = [
      h("p", { class: "config" }, h("b", {}, "Closest test configuration: "), r.config_label),
      strip(r),
      h("p", { class: "why" }, h("b", {}, "Why: "), r.why || "—"),
      r.main_gap ? h("p", { class: "gap" }, h("b", {}, "Largest gap: "), r.main_gap) : null,
    ];
    const warns = h("div", { class: "warnings" });
    renderWarnings(warns, r.warnings);
    const tags = h("div", { class: "tags" },
      h("span", { class: "tag" }, `${r.confidence} confidence`),
      inv && inv.verification_status === "human_verified" ? h("span", { class: "tag" }, "catalog checked by a person")
        : h("span", { class: "tag is-ai" }, "catalog values AI-extracted, not yet checked"),
      r.complementary ? h("span", { class: "tag" }, "tested at your oxygen") : null,
      r.tie_note ? h("span", { class: "tag" }, "near-tie, ordered by evidence quality") : null);
    const links = h("div", { class: "links" },
      link(r.psi_url, `PSI page (${r.psi_accession})`),
      link("https://doi.org/" + r.dataset_doi, `Dataset DOI ${r.dataset_doi}`),
      conf ? sourceFileLink(conf.tests_table_ref) : null,
      conf ? link(`${REPO}data/catalog/configurations.csv?plain=1#L${conf._line}`, `Catalog row (${r.config_id})`) : null,
      inv ? link(`${REPO}data/catalog/investigations.csv?plain=1#L${inv._line}`, "Investigation row") : null);
    const more = h("details", { class: "more" }, h("summary", {}, "What the record says"),
      h("p", {}, h("b", {}, "Objective (catalog summary): "), inv ? inv.objectives : "—"),
      h("p", {}, h("b", {}, "Findings stated in the record or table: "), r.key_findings || "Not stated in the PSI record."),
      card ? h("div", { class: "ai-text" }, h("p", {}, h("b", {}, "Summary: "), card.summary, " ", aiLabel(card)),
        Array.isArray(card.key_points) && card.key_points.length ? h("ul", {}, card.key_points.map((k) => h("li", {}, k.text, " ", sourceLinks(k.source, cat)))) : null)
        : h("p", { class: "gap" }, "Written summary: not available yet."),
      r.other_configs.length ? h("p", { class: "gap" }, "Other configurations in this investigation: ", r.other_configs.join(", ")) : null);
    const note = noteFor(sc, r);
    const noteEl = note ? h("div", { class: "ai-note" }, h("p", {}, h("b", {}, "Team note: "), note.text, " ", sourceLinks(note.sources, cat)), aiLabel(sc)) : null;
    ol.append(h("li", { class: "result" }, head, ...body, noteEl, warns, tags, links, more));
  }
}

function renderRanking(out) {
  const tb = $("#ranking tbody");
  tb.replaceChildren();
  const topIds = new Set(out.results.map((r) => r.investigation_id));
  out.ranking.forEach((r, i) => {
    const mini = h("span", { class: "mini", "aria-label": Object.keys(r.weights_used).map((d) => `${DIMS[d]} ${r.unknown_dims.includes(d) ? "not reported" : r.similarity[d].toFixed(2)}`).join(", ") });
    for (const d of Object.keys(r.weights_used)) {
      const unknown = r.unknown_dims.includes(d);
      const assumed = (d === "o2" && r.assumed_dims.includes("O2")) || (d === "pressure" && r.assumed_dims.includes("pressure"));
      mini.append(h("span", { class: cls(r.similarity[d], unknown, assumed), title: DIMS[d] }));
    }
    tb.append(h("tr", { class: topIds.has(r.investigation_id) ? "is-top" : null },
      h("td", { class: "num" }, String(i + 1)),
      h("td", {}, h("b", {}, r.investigation_id)),
      h("td", {}, r.config_label),
      h("td", { class: "num" }, String(r.score)),
      h("td", {}, mini),
      h("td", { class: "psi" }, link(r.psi_url, r.psi_accession)),
      h("td", { class: "psi" }, r.dataset_doi ? link("https://doi.org/" + r.dataset_doi, "DOI") : "not stated")));
  });
}


// ------------------------------------------------------------------ pipeline files
// CSV to objects, keeping the line on which each row starts (header = line 1), so a
// cell on screen can link to the exact row of the file it came from.
function parseRows(text) {
  const rows = [];
  let row = [], field = "", inQ = false, line = 1, rowLine = 1, i = 0;
  if (text.charCodeAt(0) === 0xfeff) i = 1;
  for (; i < text.length; i++) {
    const ch = text[i];
    if (inQ) {
      if (ch === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else inQ = false; }
      else { if (ch === "\n") line++; field += ch; }
    } else if (ch === '"') inQ = true;
    else if (ch === ",") { row.push(field); field = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(field); rows.push([rowLine, row]); row = []; field = ""; line++; rowLine = line;
    } else field += ch;
  }
  if (field !== "" || row.length) { row.push(field); rows.push([rowLine, row]); }
  const hdr = (rows.shift() || [0, []])[1];
  return rows.filter(([, r]) => r.length > 1 || r[0] !== "").map(([ln, r]) => {
    const o = { _line: ln };
    hdr.forEach((k, j) => { o[k] = r[j] === undefined ? "" : r[j]; });
    return o;
  });
}
const rowLink = (file, row, text, title) => h("a", { href: `${REPO}${file}?plain=1#L${row._line}`, target: "_blank", rel: "noopener", title }, text);

const PILLARS = [["prevention", "Prevention"], ["suppression", "Suppression"], ["detection", "Detection"]];
const STATUS = {
  measured: ["Measured", "st-measured", "Tests record the required conditions and an outcome for this need."],
  partial: ["Partial", "st-partial", "An outcome is recorded, but a required condition is missing."],
  conditions_only: ["Conditions only", "st-cond", "The conditions are recorded, but no outcome this need asks for."],
  none: ["Not usable", "st-none", "Tests exist, but a required condition is not recorded in any of them."],
  out_of_scope: ["Not applicable", "st-na", "Outside the scope of this need (for example, not a solid fuel)."],
  not_test_level: ["Summary rows", "st-sum", "The table's rows are test days or groups, not single tests."],
};
const VAR = (v) => v.replace(/_pct$/, " %").replace(/_kpa$/, " (kPa)").replace(/_cms$/, " (cm/s)").replace(/_/g, " ").replace(/^o2/, "O2");

function renderNeeds(out, pipe, expanded) {
  const box = $("#needs-body");
  box.replaceChildren();
  if (!pipe.matrix || !pipe.needs) { box.append(h("p", { class: "gap" }, "Needs view: not available yet.")); return; }
  const needs = pipe.needs;
  const byInv = new Map();
  for (const r of pipe.matrix) {
    if (!byInv.has(r.investigation_id)) byInv.set(r.investigation_id, new Map());
    const srcs = byInv.get(r.investigation_id);
    if (!srcs.has(r.source_id)) srcs.set(r.source_id, {});
    srcs.get(r.source_id)[r.need_id] = r;
  }
  const top = new Set(out.results.map((r) => r.psi_accession));
  const list = expanded ? out.ranking : out.ranking.filter((r) => top.has(r.psi_accession));
  const ordered = expanded ? list : out.results.map((r) => list.find((x) => x.psi_accession === r.psi_accession)).filter(Boolean);
  const focus = out.profile;

  const head1 = h("tr", {}, h("th", { rowspan: "2", scope: "col" }, "Investigation"));
  const head2 = h("tr");
  for (const [pid, plabel] of PILLARS) {
    const ns = needs.filter((n) => n.pillar === pid);
    if (!ns.length) continue;
    head1.append(h("th", { colspan: String(ns.length), scope: "colgroup", class: "pillar" + (pid === focus ? " is-focus" : "") }, plabel, pid === focus ? h("span", { class: "focus-note" }, " your question") : null));
    for (const n of ns) head2.append(h("th", { scope: "col", class: pid === focus ? "is-focus" : null, title: n.question }, n.name));
  }
  const order = PILLARS.flatMap(([pid]) => needs.filter((n) => n.pillar === pid));
  const tb = h("tbody");
  for (const r of ordered) {
    const srcs = byInv.get(r.psi_accession);
    const label = h("th", { scope: "row" }, h("b", {}, r.investigation_id), " ", h("span", { class: "acc" }, r.psi_accession));
    if (!srcs) {
      tb.append(h("tr", { class: top.has(r.psi_accession) ? "is-top" : null }, label,
        h("td", { colspan: String(order.length), class: "st-missing" }, "No experimental table in the PSI record, so the pipeline has no tests for it.")));
      continue;
    }
    const many = srcs.size > 1;
    for (const [sid, cells] of srcs) {
      const th = many ? h("th", { scope: "row" }, h("b", {}, r.investigation_id), " ", h("span", { class: "acc" }, `${r.psi_accession}, table ${sid.replace(/_/g, " ")}`)) : label;
      const tr = h("tr", { class: top.has(r.psi_accession) ? "is-top" : null }, th);
      for (const n of order) {
        const c = cells[n.id];
        if (!c) { tr.append(h("td", { class: "st-missing" }, "—")); continue; }
        const [name, cl, expl] = STATUS[c.status] || [c.status, "", ""];
        const detail = c.status === "measured" || c.status === "partial" || c.status === "conditions_only" || c.status === "none"
          ? `${c.usable_tests} of ${c.tests} tests usable` : "";
        const miss = c.required_missing ? `Missing: ${c.required_missing.split(";").map(VAR).join(", ")}` : "";
        const title = [expl, detail, miss, c.note].filter(Boolean).join(" ");
        tr.append(h("td", { class: "st " + cl + (n.pillar === focus ? " is-focus" : "") },
          rowLink("data/pipeline/capability_matrix.csv", c, name, title),
          detail ? h("small", {}, detail) : null,
          c.status === "partial" && miss ? h("small", {}, miss) : null));
      }
      tb.append(tr);
    }
  }
  box.append(h("p", { class: "scroll-hint" }, "Swipe the table sideways to see all seven needs."),
    h("div", { class: "table-wrap" }, h("table", { class: "needs-table" }, h("thead", {}, head1, head2), tb)));
  const btn = h("button", { type: "button", class: "more-btn" }, expanded ? "Show the top 3 only" : `Show all ${out.ranking.length} ranked investigations`);
  btn.addEventListener("click", () => renderNeeds(out, pipe, !expanded));
  const legend = h("dl", { class: "legend needs-legend" });
  for (const [, [name, cl, expl]] of Object.entries(STATUS)) legend.append(h("div", {}, h("dt", {}, h("span", { class: "swatch " + cl }), name), h("dd", {}, expl)));
  box.append(h("div", { class: "row-actions" }, btn), legend);

  // what each need asks, and the documents behind it
  const refs = new Map();
  for (const x of pipe.refs || []) {
    if (!refs.has(x.need_id)) refs.set(x.need_id, new Map());
    const m = refs.get(x.need_id);
    if (!m.has(x.reference_id)) m.set(x.reference_id, x);
  }
  const defs = h("dl", { class: "need-defs" });
  for (const n of order) {
    const docs = [...(refs.get(n.id) || new Map()).values()];
    defs.append(h("dt", {}, `${n.name} (${n.id})`),
      h("dd", {}, n.question, " ", h("span", { class: "gap" }, "Needs: ", (n.conditions_required || []).map(VAR).join(", "), "."),
        docs.length ? h("span", { class: "basis" }, " Basis: ", ...docs.flatMap((d, i) => [i ? "; " : "", d.url ? link(d.url, d.reference_id) : d.reference_id])) : null));
  }
  box.append(h("details", { class: "more" }, h("summary", {}, "What each need asks, and the documents behind it"),
    defs, h("p", { class: "gap" }, "Definitions: ", link(REPO + "pipeline/spec/needs.json", "pipeline/spec/needs.json"), "; document items: ",
      link(REPO + "data/pipeline/need_references.csv", "data/pipeline/need_references.csv"), ". Written with AI assistance by the team's data role; not yet reviewed by a person.")));
}


function renderScenarioText(out, sc, cat) {
  const other = $("#other-notes");
  other.replaceChildren();
  const needsBox = $("#needs-notes");
  needsBox.replaceChildren();
  const gapsBox = $("#gaps");
  gapsBox.replaceChildren();
  $("#gaps-section").hidden = true;
  if (!sc) return;
  const top = new Set(out.results.flatMap((r) => [r.psi_accession, r.investigation_id]));
  const rest = (sc.result_notes || []).filter((n) => !top.has(n.investigation_id));
  if (rest.length) other.append(h("h3", {}, "Other investigations"), h("ul", { class: "ai-list" },
    rest.map((n) => h("li", {}, h("b", {}, n.investigation_id), ": ", n.text, " ", sourceLinks(n.sources, cat)))), aiLabel(sc));
  if (Array.isArray(sc.needs) && sc.needs.length) needsBox.append(h("h3", {}, "For this scenario"),
    h("ul", { class: "ai-list" }, sc.needs.map((n) => h("li", {}, h("b", {}, n.need_id), ": ", n.statement, " ", sourceLinks(n.sources, cat)))), aiLabel(sc));
  if (Array.isArray(sc.gaps) && sc.gaps.length) {
    gapsBox.append(h("ul", { class: "ai-list" }, sc.gaps.map((g) => h("li", {}, g.text, g.needed_data ? h("span", { class: "gap" }, " Data that would close it: ", g.needed_data) : null))), aiLabel(sc));
    $("#gaps-section").hidden = false;
  }
}

function binOf(bins, v) {
  if (typeof v !== "number" || Number.isNaN(v)) return null;
  return bins.find((b) => (b.min === null || (b.min_inclusive ? v >= b.min : v > b.min)) &&
    (b.max === null || (b.max_inclusive ? v <= b.max : v < b.max))) || null;
}
const splitLabel = (l) => { const i = l.indexOf(" ("); return i < 0 ? [l, ""] : [l.slice(0, i), l.slice(i + 2, -1)]; };

function renderCoverage(out, pipe) {
  const box = $("#coverage-body");
  box.replaceChildren();
  if (!pipe.grid || !pipe.coverage) { box.append(h("p", { class: "gap" }, "Coverage view: not available yet.")); return; }
  const dims = pipe.coverage.dimensions;
  const NR = pipe.coverage.not_recorded || { id: "not_recorded", label: "not recorded" };
  const o2bins = [...dims.o2_pct.bins, NR];
  const pbins = [...dims.pressure_kpa.bins, NR];
  const sc = out.scenario;
  const o2b = binOf(dims.o2_pct.bins, sc.o2_pct);
  const pb = binOf(dims.pressure_kpa.bins, sc.pressure_kpa);
  const phases = ["solid", "liquid", "gas"];
  const userPhase = phases.includes(sc.fuel_phase) ? sc.fuel_phase : null;
  const order = userPhase ? [userPhase, ...phases.filter((p) => p !== userPhase)] : phases;
  const FILE = "data/pipeline/coverage_grid.csv";
  const max = Math.max(1, ...pipe.grid.filter((r) => r.o2_basis === "ambient").map((r) => +r.tests || 0));

  if (!o2b || !pb) box.append(h("p", { class: "warn" }, "Your input has no ", !o2b && !pb ? "oxygen or pressure" : !o2b ? "oxygen" : "pressure",
    " value, so it is not marked on the grids. Add it to the question, for example 30% O2 at 70 kPa."));

  for (const ph of order) {
    const rows = pipe.grid.filter((r) => r.fuel_phase === ph && r.o2_basis === "ambient");
    const cell = (o, p) => rows.find((r) => r.o2_bin === o && r.pressure_bin === p);
    const block = h("div", { class: "cov-block" });
    const title = h("h3", {}, `${ph[0].toUpperCase()}${ph.slice(1)} fuels`, ph === userPhase ? h("span", { class: "focus-note" }, " your fuel") : null);
    block.append(title);
    if (o2b) {
      const atO2 = rows.filter((r) => r.o2_bin === o2b.id);
      const any = atO2.reduce((a, r) => a + (+r.tests || 0), 0);
      const inCell = pb ? cell(o2b.id, pb.id) : null;
      const noP = cell(o2b.id, NR.id);
      const s = h("p", { class: "cov-sum" + (any === 0 ? " is-thin" : "") },
        h("b", {}, `At ${splitLabel(o2b.label)[0]} oxygen: `),
        atO2.length ? h("a", { href: `${REPO}${FILE}?plain=1#L${Math.min(...atO2.map((r) => r._line))}-L${Math.max(...atO2.map((r) => r._line))}`,
          target: "_blank", rel: "noopener", title: "Sum of these rows of the coverage grid" }, String(any)) : String(any),
        ` recorded test${any === 1 ? "" : "s"} at any pressure`);
      if (any > 0 && pb && inCell) s.append(", ", rowLink(FILE, inCell, `${inCell.tests}`), ` in your pressure bin (${splitLabel(pb.label)[0]})`);
      if (noP && +noP.tests > 0) s.append(", ", rowLink(FILE, noP, `${noP.tests}`), " with no pressure recorded");
      s.append(".");
      block.append(s);
    }
    const thead = h("tr", {}, h("th", { scope: "col", class: "corner" }, "Oxygen ↓  Pressure →"));
    for (const p of pbins) {
      const [a, b] = splitLabel(p.label);
      thead.append(h("th", { scope: "col", class: (p.id === NR.id ? "nr" : "") + (pb && p.id === pb.id ? " is-you" : "") }, a, b ? h("small", {}, b) : null));
    }
    const tb = h("tbody");
    for (const o of [...o2bins.slice(0, -1)].reverse().concat([NR])) {
      const [a, b] = splitLabel(o.label);
      const tr = h("tr", {}, h("th", { scope: "row", class: (o.id === NR.id ? "nr" : "") + (o2b && o.id === o2b.id ? " is-you" : "") }, a, b ? h("small", {}, b) : null));
      for (const p of pbins) {
        const r = cell(o.id, p.id);
        const you = o2b && pb && o.id === o2b.id && p.id === pb.id;
        if (!r) { tr.append(h("td", { class: "c-none" + (you ? " is-target" : "") }, "—")); continue; }
        const n = +r.tests || 0;
        const lvl = n === 0 ? 0 : Math.min(4, 1 + Math.floor(3 * Math.log(n) / Math.log(max)));
        const tip = n ? `${n} tests: ${r.investigation_ids.split(";").join(", ")}` : "No recorded test";
        tr.append(h("td", { class: `c-l${lvl}` + (o.id === NR.id || p.id === NR.id ? " c-nr" : "") + (you ? " is-target" : "") },
          rowLink(FILE, r, String(n), tip), you ? h("small", {}, "your input") : null,
          n ? h("small", { class: "ids" }, r.investigation_ids.split(";").join(", ")) : null));
      }
      tb.append(tr);
    }
    block.append(h("p", { class: "scroll-hint" }, "Swipe the grid sideways to see every pressure."),
      h("div", { class: "table-wrap" }, h("table", { class: "cov-table" }, h("thead", {}, thead), tb)));
    const others = pipe.grid.filter((r) => r.fuel_phase === ph && r.o2_basis !== "ambient" && +r.tests > 0);
    const byBasis = new Map();
    for (const r of others) { if (!byBasis.has(r.o2_basis)) byBasis.set(r.o2_basis, []); byBasis.get(r.o2_basis).push(r); }
    for (const [basis, rs] of byBasis) {
      const n = rs.reduce((a, r) => a + (+r.tests || 0), 0);
      const ids = [...new Set(rs.flatMap((r) => r.investigation_ids.split(";")))].join(", ");
      block.append(h("p", { class: "gap" }, `Not in this grid: ${n} ${ph}-fuel tests `,
        basis === "oxidizer_stream" ? "where the oxygen value is the burner stream of an inverse flame, not the surrounding atmosphere" : "whose table has no oxygen column",
        ` (${ids}; `, rowLink(FILE, rs[0], "first row"), ")."));
    }
    if (ph === userPhase || !userPhase) box.append(block);
    else box.append(h("details", { class: "more cov-other" }, h("summary", {}, `${ph[0].toUpperCase()}${ph.slice(1)} fuels`), block));
  }
  box.append(h("p", { class: "gap" }, "Bins: ", link(REPO + "pipeline/spec/coverage.json", "pipeline/spec/coverage.json"),
    ". Counts: ", link(REPO + FILE, FILE), ", built from ", link(REPO + "data/pipeline/tests.csv", "data/pipeline/tests.csv"), " by the team's pipeline."));
}

function show(id, on) { $(id).hidden = !on; }
function setStatus(text, kind) {
  const s = $("#status");
  s.className = "status" + (kind ? " is-" + kind : "");
  s.textContent = text || "";
}

async function loadJSON(path, fallback) {
  try { const r = await fetch(path); if (!r.ok) throw new Error(r.status); return await r.json(); }
  catch (e) { if (fallback !== undefined) return fallback; throw e; }
}
async function loadText(path) { const r = await fetch(path); if (!r.ok) throw new Error(`${path}: ${r.status}`); return r.text(); }

async function main() {
  setStatus("Loading the catalog…");
  let config, scorer, invOrder = [], insights = { cards: {} };
  try {
    const [cfg, invCsv, cfgCsv, cards, build] = await Promise.all([
      loadJSON("data/scoring_config.json"), loadText("data/investigations.csv"), loadText("data/configurations.csv"),
      loadJSON("data/insights/cards.json", null), loadJSON("data/build.json", null)]);
    insights.scenarios = await loadJSON("data/insights/scenarios.json", []);
    if (!Array.isArray(insights.scenarios)) insights.scenarios = [];
    if (build && /^[0-9a-f]{7,40}$/.test(build.commit)) REPO = REPO_BASE + build.commit + "/";
    config = cfg;
    scorer = createScorer({ config, investigationsCsv: invCsv, configurationsCsv: cfgCsv });
    invOrder = parseCSV(invCsv).map((row) => row.investigation_id);
    if (Array.isArray(cards)) for (const c of cards) insights.cards[c.investigation_id] = c;
  } catch (e) {
    setStatus("The catalog could not be loaded. Reload the page; if it persists, the site files are incomplete.", "error");
    return;
  }
  setStatus("");
  const cat = scorer.catalog;
  const optText = (p) => loadText(p).catch(() => null);
  const [mx, nd, gr, cv, rf] = await Promise.all([optText("data/capability_matrix.csv"), loadJSON("data/needs.json", null),
    optText("data/coverage_grid.csv"), loadJSON("data/coverage.json", null), optText("data/need_references.csv")]);
  const parseList = (v) => Array.isArray(v) ? v : typeof v === "string" ? v.replace(/[\[\]']/g, "").split(",").map((x) => x.trim()).filter(Boolean) : [];
  const pipe = {
    matrix: mx ? parseRows(mx) : null,
    needs: nd && Array.isArray(nd.needs) ? nd.needs.map((n) => ({ ...n, conditions_required: parseList(n.conditions_required) })) : null,
    grid: gr ? parseRows(gr) : null,
    coverage: cv,
    refs: rf ? parseRows(rf) : null,
  };
  // line numbers in the CSV files (header is line 1), for links to the exact source row
  cat.configurations.forEach((c, i) => { c._line = i + 2; });
  Object.values(cat.investigations).forEach((v) => { v._line = invOrder.indexOf(v.investigation_id) + 2; });

  function run(q, push = true) {
    $("#q").value = q;
    document.querySelectorAll(".presets button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.q === q)));
    const out = scorer.rank(q);
    if (push) {
      const url = new URL(location.href);
      url.searchParams.set("q", q);
      history.replaceState(null, "", url);
    }
    show("#read", true);
    renderConditions(out, config);
    renderAssumptions(out, config);
    renderWarnings($("#scenario-warnings"), out.warnings);
    if (out.status !== "ok") {
      show("#top", false); show("#all", false); show("#needs", false); show("#coverage", false); show("#gaps-section", false);
      $("#assumptions").replaceChildren();
      setStatus(out.status === "out_of_scope" ? "Out of scope for this tool." : "Add an environment or a material to start.", "info");
      return;
    }
    setStatus("");
    const sc = scenarioNotes(q, out, insights);
    renderResults(out, cat, insights, sc);
    renderScenarioText(out, sc, cat);
    renderRanking(out);
    renderNeeds(out, pipe, false);
    renderCoverage(out, pipe);
    show("#top", true); show("#all", true); show("#needs", true); show("#coverage", true);
  }

  $("#ask-form").addEventListener("submit", (e) => { e.preventDefault(); run($("#q").value.trim()); });
  document.querySelectorAll(".presets button").forEach((b) => b.addEventListener("click", () => run(b.dataset.q)));
  const q0 = new URL(location.href).searchParams.get("q");
  run(q0 !== null ? q0 : "ISS", q0 !== null);
}

main();
