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
// Element.append(null) prints the word "null": append only real children.
const put = (el, ...kids) => el.append(...kids.flat().filter((k) => k !== null && k !== undefined && k !== false));

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
// Three kinds of text, labelled honestly (pm request 1224, item 2): quoted from NASA,
// computed by team code from fixed templates, or written by a language model.
const isQuote = (c) => Boolean(c) && (c.status === "fallback_quote" || c.ai_generated === false);
const isTemplate = (x, sc) => ((x && x.text_origin) || (sc && sc.text_origin)) === "template";
const quoteTag = () => h("span", { class: "tag" }, "Quoted from the PSI record");
const computedTag = () => h("span", { class: "tag" }, "Computed by team code from NASA PSI tables");
const cardTag = (c) => (isQuote(c) ? quoteTag() : aiLabel(c));
const itemTag = (x, sc) => (isTemplate(x, sc) ? computedTag() : aiLabel(sc));
// One label after a list when every item has the same origin; otherwise one per item.
function listLabel(items, sc) {
  const t = items.filter((x) => isTemplate(x, sc)).length;
  if (t === items.length) return { inline: false, tag: computedTag() };
  if (t === 0) return { inline: false, tag: aiLabel(sc) };
  return { inline: true, tag: null };
}
function scenarioNotes(query, out, insights) {
  const q = query.trim().toLowerCase();
  return (insights.scenarios || []).find((e) => typeof e.query === "string" && e.query.trim().toLowerCase() === q && e.id === out.scenario.preset) || null;
}
function noteFor(sc, r) {
  if (!sc || !Array.isArray(sc.result_notes)) return null;
  return sc.result_notes.find((n) => n.investigation_id === r.psi_accession || n.investigation_id === r.investigation_id) || null;
}

const VIDEO_PILOT = "Side pilot (AI-written code; frames checked by an AI assistant, not by a person): for 19 BASS-II clips (PSI-25) we copied the numbers NASA's video shows on screen (FUEL, AIR, FAN, RAD, clock) into one row per second. This is a transcription of NASA's display, not a NASA data file and not a team measurement. About 750 values were compared with the picture and none was wrong. It gives no flame-out time and no flow speed at blowoff or extinction.";
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
      card ? h("div", { class: "ai-text" }, h("p", {}, h("b", {}, "Summary: "), card.summary, " ",
        Array.isArray(card.summary_sources) && card.summary_sources.length ? [sourceLinks(card.summary_sources, cat), " "] : null, cardTag(card)),
        Array.isArray(card.key_points) && card.key_points.length ? h("ul", {}, card.key_points.map((k) => h("li", {}, k.text, " ", sourceLinks(k.source, cat)))) : null)
        : h("p", { class: "gap" }, "Written summary: not available yet."),
      r.other_configs.length ? h("p", { class: "gap" }, "Other configurations in this investigation: ", r.other_configs.join(", ")) : null);
    const rawSentence = insights.raw && insights.raw.sentences ? insights.raw.sentences[r.psi_accession] : null;
    const rawLine = rawSentence ? h("p", { class: "raw-line" }, h("b", {}, "Raw data in PSI: "), rawSentence, " ",
      link(REPO + insights.raw.source, "(team count from the PSI file listing)")) : null;
    // pm request 1709: the video side pilot, one sentence word for word, next to PSI-25's raw-data line.
    // No number from the pilot's files is read by the page.
    const videoEl = rawLine && r.psi_accession === "PSI-25" && OPTIONAL_HAS("repo:video/README.md")
      ? h("p", { class: "raw-line" }, VIDEO_PILOT, " ", link(REPO + "video/README.md", "(video/README.md)")) : null;
    const robust = robustLine(insights.robustRun, r);
    const robustEl = robust ? h("p", { class: "raw-line rob-line" }, h("b", {}, "Weight check: "), robust, " ",
      h("a", { href: "#ai-use" }, "(team computation)")) : null;
    const note = noteFor(sc, r);
    const noteEl = note ? h("div", { class: "ai-note" }, h("p", {}, h("b", {}, "Team note: "), note.text, " ", sourceLinks(note.sources, cat)), itemTag(note, sc)) : null;
    ol.append(h("li", { class: "result" }, head, ...body, noteEl, warns, tags, links, rawLine, videoEl, robustEl, more));
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
// Decision 10 (coord/decisions.md, 11/14 12:15): a test is evidence for a need only when the
// investigation's PSI record states that need as an objective (objective_link = stated).
const OUTSIDE = ["Outside stated objective", "st-outside",
  "Recorded, outside the investigation's stated objective: the PSI record does not name this need as an aim, so these tests are not counted as evidence."];
const RECORDED = new Set(["measured", "partial", "conditions_only", "none"]);
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
  const srow = scenarioNeedsRow(out, pipe, order);
  if (srow) tb.append(srow);
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
        const outside = c.objective_link === "not_stated" && RECORDED.has(c.status);
        const [stName, , stExpl] = STATUS[c.status] || [c.status, "", ""];
        const [name, cl, expl] = outside ? OUTSIDE : STATUS[c.status] || [c.status, "", ""];
        const detail = RECORDED.has(c.status)
          ? outside ? `${c.tests} tests recorded, not counted` : `${c.usable_tests} of ${c.tests} tests usable` : "";
        const miss = c.required_missing ? `Missing: ${c.required_missing.split(";").map(VAR).join(", ")}` : "";
        const quote = c.objective_link === "stated" && c.objective_quote ? `Stated objective: "${c.objective_quote}"` : "";
        const title = [expl, outside ? `Pipeline status without the objective rule: ${stName}. ${stExpl}` : "", detail, miss, quote, c.note].filter(Boolean).join(" ");
        tr.append(h("td", { class: "st " + cl + (n.pillar === focus ? " is-focus" : "") },
          rowLink("data/pipeline/capability_matrix.csv", c, name, title),
          detail ? h("small", {}, detail) : null,
          c.status === "partial" && miss && !outside ? h("small", {}, miss) : null));
      }
      tb.append(tr);
    }
  }
  box.append(h("p", { class: "scroll-hint" }, `Swipe the table sideways to see all ${order.length} needs.`),
    h("div", { class: "table-wrap" }, h("table", { class: "needs-table" }, h("thead", {}, head1, head2), tb)));
  if (srow) {
    // What a count in the first row means and does not mean (data's needs.json "reading").
    const rd = order.filter((n) => typeof n.reading === "string" && n.reading);
    if (rd.length) box.append(h("details", { class: "more readings", open: "" }, h("summary", {}, "What the counts in the first row mean"),
      h("dl", { class: "need-defs" }, rd.flatMap((n) => [h("dt", {}, `${n.name} (${n.id})`), h("dd", {}, n.reading)])),
      h("p", { class: "gap" }, "Readings: ", link(REPO + "pipeline/spec/needs.json", "pipeline/spec/needs.json"), ", written by the team's data role.")));
  }
  const btn = h("button", { type: "button", class: "more-btn" }, expanded ? "Show the top 3 only" : `Show all ${out.ranking.length} ranked investigations`);
  btn.addEventListener("click", () => renderNeeds(out, pipe, !expanded));
  const legend = h("dl", { class: "legend needs-legend" });
  for (const [name, cl, expl] of [...Object.values(STATUS).slice(0, 4), OUTSIDE, ...Object.values(STATUS).slice(4)])
    legend.append(h("div", {}, h("dt", {}, h("span", { class: "swatch " + cl }), name), h("dd", {}, expl)));
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
        typeof n.reading === "string" && n.reading ? h("span", { class: "gap" }, " What a count means: ", n.reading) : null,
        docs.length ? h("span", { class: "basis" }, " Basis: ", ...docs.flatMap((d, i) => [i ? "; " : "", d.url ? link(d.url, d.reference_id) : d.reference_id])) : null));
  }
  box.append(h("details", { class: "more" }, h("summary", {}, "What each need asks, and the documents behind it"),
    defs, h("p", { class: "gap" }, "Definitions: ", link(REPO + "pipeline/spec/needs.json", "pipeline/spec/needs.json"), "; document items: ",
      link(REPO + "data/pipeline/need_references.csv", "data/pipeline/need_references.csv"), ". Written with AI assistance by the team's data role; not yet reviewed by a person.")));
}


function renderScenarioText(out, sc, cat) {
  const other = $("#other-notes");
  other.replaceChildren();
  const frameBox = $("#scenario-frame");
  frameBox.replaceChildren();
  const needsBox = $("#needs-notes");
  needsBox.replaceChildren();
  const gapsBox = $("#gaps");
  gapsBox.replaceChildren();
  $("#gaps-section").hidden = true;
  if (!sc) return;
  const top = new Set(out.results.flatMap((r) => [r.psi_accession, r.investigation_id]));
  const rest = (sc.result_notes || []).filter((n) => !top.has(n.investigation_id));
  if (rest.length) {
    const L = listLabel(rest, sc);
    put(other, h("h3", {}, "Other investigations"), h("ul", { class: "ai-list" },
      rest.map((n) => h("li", {}, h("b", {}, n.investigation_id), ": ", n.text, " ", sourceLinks(n.sources, cat), L.inline ? [" ", itemTag(n, sc)] : null))), L.tag);
  }
  // The scenario's frame (ranges, gravity, what PSI cannot say) sits above the need list.
  if (typeof sc.frame === "string" && sc.frame.trim()) {
    const fx = { text_origin: sc.frame_text_origin || sc.text_origin };
    // Long frames (the lunar one is ~540 words): first two sentences, the rest folded (pm request 1622).
    const sents = sc.frame.match(/[^.!?]+(?:[.!?]+(?=\s|$)|$)/g) || [sc.frame];
    const lead = sents.slice(0, 2).join("").trim(), rest = sents.slice(2).join("").trim();
    frameBox.append(h("div", { class: "frame" }, h("p", {}, lead, " ",
      Array.isArray(sc.frame_sources) && sc.frame_sources.length ? [sourceLinks(sc.frame_sources, cat), " "] : null, itemTag(fx, sc)),
      rest ? h("details", { class: "more" }, h("summary", {}, "Read the rest of the frame"), h("p", {}, rest)) : null));
  }
  if (Array.isArray(sc.needs) && sc.needs.length) {
    const L = listLabel(sc.needs, sc);
    put(needsBox, h("h3", {}, "For this scenario"),
      h("ul", { class: "ai-list" }, sc.needs.map((n) => h("li", {}, h("b", {}, n.need_id), ": ", n.statement, " ", sourceLinks(n.sources, cat), L.inline ? [" ", itemTag(n, sc)] : null))), L.tag);
  }
  if (Array.isArray(sc.gaps) && sc.gaps.length) {
    const L = listLabel(sc.gaps, sc);
    put(gapsBox, h("ul", { class: "ai-list" }, sc.gaps.map((g) => h("li", {}, g.text,
      Array.isArray(g.sources) && g.sources.length ? [" ", sourceLinks(g.sources, cat)] : null,
      g.needed_data ? h("span", { class: "gap" }, " Data that would close it: ", g.needed_data) : null,
      L.inline ? [" ", itemTag(g, sc)] : null))), L.tag);
    $("#gaps-section").hidden = false;
  }
}


// ------------------------------------------------------------------ scenario matching (data role)
// "In your atmosphere" means tests were run there, not that the need is covered: for the lunar
// habitat those are fuel-droplet tests (pm request 1224), so it is not drawn as a full cell.
const SN_STATUS = {
  in_atmosphere: ["Tests in the scenario range", "st-partial"],
  oxygen_only: ["At your oxygen, pressure not recorded", "st-cond"],
  pressure_only: ["At your pressure, oxygen not recorded", "st-cond"],
  other_atmosphere: ["Only other atmospheres", "st-sum"],
  not_measured: ["No usable test", "st-none"],
};
// The dashboard shows only the two demo scenarios; data's other scenarios feed pm's text.
const DASH_SCENARIOS = new Set(["iss", "lunar_habitat"]);
// data request 1242, item 12: where the NASA table has no oxygen or pressure column, say so
// instead of "Only other atmospheres".
function otherAtmosphereLabel(gaps) {
  const o2Missing = gaps.includes("oxygen:not_recorded"), pMissing = gaps.includes("pressure:not_recorded");
  if (o2Missing && pMissing) return "Oxygen and pressure not in the NASA table";
  if (o2Missing) return gaps.some((g) => g.startsWith("pressure:")) ? "Other pressure; oxygen not in the NASA table" : "Oxygen not in the NASA table";
  if (pMissing) return gaps.some((g) => g.startsWith("oxygen:")) ? "Other oxygen; pressure not in the NASA table" : "Pressure not in the NASA table";
  return null;
}
const TIERS = [
  ["atmosphere", "In the scenario range", "oxygen and pressure both recorded and inside the scenario's ranges"],
  ["oxygen_only", "At your oxygen, no pressure recorded", "oxygen inside the range; the table records no pressure"],
  ["pressure_only", "At your pressure, no oxygen recorded", "pressure inside the range; the table records no oxygen"],
];
// Known gap codes in words; an unknown code is shown as the code itself (data request 1242, item 10).
function gapWords(code) {
  const [v, why] = code.split(":");
  const NAMES = { oxygen: "oxygen", pressure: "pressure", gravity: "gravity", flow: "flow" };
  if (v === "need" && why === "no_usable_test") return "no usable test for this need";
  const name = NAMES[v];
  if (!name || !why) return code;
  if (why === "not_recorded") return `${name} not recorded`;
  if (why === "no_usable_test_in_range") return `no usable test at your ${name}`;
  const m = /^no_usable_test_at_(.+)$/.exec(why);
  if (m) return `no test at ${m[1]} ${name}`;
  return code;
}
function scenarioId(out, pipe) {
  const id = out.scenario.preset;
  return id && DASH_SCENARIOS.has(id) && pipe.scenarioSpec && pipe.scenarioSpec.scenarios.some((x) => x.id === id) ? id : null;
}
function rangeText(r, unit) {
  if (!r) return "any";
  const lo = r.min === null || r.min === undefined ? null : r.min, hi = r.max === null || r.max === undefined ? null : r.max;
  if (lo !== null && hi !== null) return `${lo} to ${r.max_inclusive ? "" : "below "}${hi}${unit}`;
  if (lo !== null) return `${lo}${unit} or more`;
  return `${r.max_inclusive ? "up to " : "below "}${hi}${unit}`;
}
function scenarioRanges(spec) {
  const r = spec.ranges || {};
  const parts = [`oxygen ${rangeText(r.o2_pct, "%")}`, `pressure ${rangeText(r.pressure_kpa, " kPa")}`];
  if (r.flow_cms) parts.push(`flow ${rangeText(r.flow_cms, " cm/s")}`);
  if (spec.gravity_level) parts.push(/gravity$/.test(spec.gravity_level) ? spec.gravity_level : `${spec.gravity_level} gravity`);
  return parts.join(", ");
}

function scenarioNeedsRow(out, pipe, order) {
  const sid = scenarioId(out, pipe);
  if (!sid || !pipe.scenarioNeeds) return null;
  const rows = pipe.scenarioNeeds.filter((r) => r.scenario_id === sid);
  if (!rows.length) return null;
  const spec = pipe.scenarioSpec.scenarios.find((x) => x.id === sid);
  const tr = h("tr", { class: "scenario-row" }, h("th", { scope: "row" }, h("b", {}, "All tables, in the scenario range"),
    h("small", {}, scenarioRanges(spec)),
    spec.caveat ? h("small", { class: "caveat" }, spec.caveat) : null));
  for (const n of order) {
    const r = rows.find((x) => x.need_id === n.id);
    if (!r) { tr.append(h("td", { class: "st-missing" }, "—")); continue; }
    const [baseName, cl] = SN_STATUS[r.status] || [r.status, ""];
    const codes = r.gaps ? r.gaps.split(";").filter(Boolean) : [];
    const name = (r.status === "other_atmosphere" && otherAtmosphereLabel(codes)) || baseName;
    const tierN = r.status === "in_atmosphere" ? r.tests_atmosphere : r.status === "oxygen_only" ? r.tests_oxygen_only
      : r.status === "pressure_only" ? r.tests_pressure_only : null;
    const invs = r.status === "in_atmosphere" ? r.investigations_atmosphere : r.status === "oxygen_only" ? r.investigations_oxygen_only
      : r.status === "pressure_only" ? r.investigations_pressure_only : "";
    const gaps = codes.map(gapWords);
    const outsideN = +r.tests_recorded_outside_objective || 0;
    const addedGasN = +r.matched_tests_co2_or_helium_added || 0;
    tr.append(h("td", { class: "st " + cl, title: [`${r.usable_tests} usable tests for this need in all tables, counted only where the investigation states this need as an objective.`, n.reading || ""].filter(Boolean).join(" ") },
      rowLink("data/pipeline/scenario_needs.csv", r, name),
      tierN !== null ? h("small", {}, `${tierN} of ${r.usable_tests} usable tests${invs ? ", " + invs.split(";").join(", ") : ""}`)
        : r.status === "not_measured" ? null : h("small", {}, `${r.usable_tests} usable tests elsewhere`),
      tierN !== null && addedGasN ? h("small", {}, `${addedGasN} of ${(+r.tests_atmosphere || 0) + (+r.tests_oxygen_only || 0) + (+r.tests_pressure_only || 0)} matched tests had carbon dioxide or helium added`) : null,
      outsideN ? h("small", {}, `${outsideN} more recorded outside the stated objective, not counted`) : null,
      gaps.length ? h("small", { class: "gaps-codes" }, gaps.join("; ")) : null));
  }
  return tr;
}

// test_id -> row of the slim data/tests.csv written by web/build.py (test_id, source_file,
// source_row, o2_pct, pressure_kpa, line = the row's line in data/pipeline/tests.csv). Loaded once.
// ISS and lunar habitat side by side: the demo's contrast in one glance, from scenario_needs.csv.
const COMPARE = [["iss", "ISS"], ["lunar_habitat", "lunar habitat"]]; // [scenario id, query the button runs]
const SN_SHORT = { in_atmosphere: "in range", oxygen_only: "O2 in range, no pressure in table", pressure_only: "pressure in range, no O2 in table",
  other_atmosphere: "other atmospheres only", not_measured: "no usable test" };
function renderCompare(out, pipe, runQuery) {
  const box = $("#compare");
  box.replaceChildren();
  const sid = scenarioId(out, pipe);
  if (!sid || !pipe.scenarioNeeds || !pipe.needs || !COMPARE.some(([id]) => id === sid)) return;
  const order = PILLARS.flatMap(([pid]) => pipe.needs.filter((n) => n.pillar === pid));
  const specOf = (id) => pipe.scenarioSpec.scenarios.find((x) => x.id === id) || { id, label: id };
  const thead = h("tr", {}, h("th", { scope: "col" }, "Scenario"), ...order.map((n) => h("th", { scope: "col", title: n.question }, n.name)));
  const tb = h("tbody");
  const summary = [];
  for (const [id, q] of COMPARE) {
    const spec = specOf(id);
    const rows = pipe.scenarioNeeds.filter((r) => r.scenario_id === id);
    if (!rows.length) continue;
    const mine = id === sid;
    const btn = mine ? h("span", { class: "tag" }, "your query") : h("button", { type: "button", class: "more-btn compare-go" }, `Show "${q}"`);
    if (!mine) btn.addEventListener("click", () => runQuery(q));
    const tr = h("tr", { class: mine ? "is-you" : null }, h("th", { scope: "row" }, h("b", {}, spec.label || id), " ", btn));
    let withTests = 0;
    for (const n of order) {
      const r = rows.find((x) => x.need_id === n.id);
      if (!r) { tr.append(h("td", { class: "st-missing" }, "—")); continue; }
      const atm = +r.tests_atmosphere || 0, o2o = +r.tests_oxygen_only || 0, po = +r.tests_pressure_only || 0;
      const matched = atm + o2o + po;
      if (matched) withTests++;
      const codes = r.gaps ? r.gaps.split(";").filter(Boolean) : [];
      const parts = [atm ? `${atm} in range` : "", o2o ? `${o2o} with O2 in range, no pressure in table` : "", po ? `${po} with pressure in range, no O2 in table` : ""].filter(Boolean);
      const word = parts.length ? parts.join("; ") : (r.status === "other_atmosphere" && otherAtmosphereLabel(codes)) || SN_SHORT[r.status] || r.status;
      const [, cl] = SN_STATUS[r.status] || ["", ""];
      tr.append(h("td", { class: "st " + cl }, rowLink("data/pipeline/scenario_needs.csv", r, String(matched), `${matched} counted tests matched to this scenario's range for ${n.name}.`), h("small", {}, word)));
    }
    tb.append(tr);
    summary.push(`${spec.label || id}: matched tests for ${withTests} of ${order.length} needs`);
  }
  const caveats = COMPARE.map(([id]) => specOf(id)).filter((s) => s.caveat).map((s) => h("li", {}, h("b", {}, `${s.label}: `), s.caveat));
  put(box, h("h3", {}, "ISS and lunar habitat, side by side"),
    h("p", { class: "team-note" }, "Counted recorded tests matched to each scenario's oxygen and pressure range, per need (counted only where the investigation states the need as an objective). Team computation from the PSI tables."),
    h("div", { class: "table-wrap" }, h("table", { class: "compare-table" }, h("thead", {}, thead), tb)),
    h("p", { class: "cov-sum" }, summary.join(". ") + "."),
    caveats.length ? h("ul", { class: "gap compare-caveats" }, caveats) : null);
}

// The slim scenario_tests.csv, fetched once and shared by the tests list and the export box.
function scenarioTestsOf(pipe) {
  if (!pipe.scenarioTestsP) pipe.scenarioTestsP = loadText("data/scenario_tests.csv").then(parseRows).catch((e) => { pipe.scenarioTestsP = null; throw e; });
  return pipe.scenarioTestsP;
}

// Find · "Take the data with you" (pm request 1449): downloads with their NASA sources, and the
// dataset DOI of every investigation in them, because PSI asks to be cited by DOI.
async function renderExport(out, pipe, cat) {
  const box = $("#export");
  box.replaceChildren();
  if (out.status !== "ok") return;
  const RAW = REPO.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob/", "/");
  const sid = scenarioId(out, pipe);
  const spec = sid && pipe.scenarioSpec ? pipe.scenarioSpec.scenarios.find((x) => x.id === sid) : null;
  const exportFile = sid ? `data/export/scenario_${sid}_matched_tests.csv` : null;
  let accs = out.results.map((r) => r.psi_accession);
  const items = [];
  if (exportFile && OPTIONAL_HAS(exportFile)) {
    try {
      const rows = (await scenarioTestsOf(pipe)).filter((r) => r.scenario_id === sid && r.tier !== "other");
      accs = [...new Set([...accs, ...rows.map((r) => r.investigation_id)])]; // the top 3 and every investigation in the file
      items.push(h("li", {}, h("a", { href: vurl(exportFile), download: `${sid}_matched_tests.csv` }, `Matched tests for ${spec ? spec.label : sid} (CSV, ${rows.length} tests)`),
        h("span", { class: "gap" }, ": each test's tier, recorded oxygen, pressure and flow, flags, and its NASA source file and row.")));
    } catch (e) { /* the list below still offers the full files */ }
  }
  if (sid && OPTIONAL_HAS(`repo:data/pipeline/evidence/scenario_${sid}.json`))
    items.push(h("li", {}, link(`${RAW}data/pipeline/evidence/scenario_${sid}.json`, `Evidence package for ${spec ? spec.label : sid} (JSON)`),
      h("span", { class: "gap" }, ": per need, the matched tests with values, units, source columns and rows, built by the team's data role.")));
  items.push(h("li", {}, link(`${RAW}data/pipeline/tests.csv`, "All recorded tests (CSV, one row per test)"), h("span", { class: "gap" }, " and "),
    link(`${RAW}data/pipeline/values_long.csv`, "every value with its source column (CSV)"), "."));
  const invOf = (acc) => Object.values(cat.investigations).find((v) => v.psi_accession === acc);
  const cites = accs.map(invOf).filter(Boolean).sort((a, b) => a.investigation_id.localeCompare(b.investigation_id));
  put(box, h("h3", {}, "Take the data with you"), h("ul", { class: "export-list" }, items),
    cites.length ? h("details", { class: "more cite" }, h("summary", {}, `How to cite: ${cites.length} NASA PSI dataset${cites.length === 1 ? "" : "s"} (the top results${exportFile && OPTIONAL_HAS(exportFile) ? " and the matched-tests download" : ""})`),
      h("ul", { class: "cite-list" }, cites.map((v) => h("li", {}, `${v.investigation_name} (${v.investigation_id}, ${v.psi_accession}). NASA Physical Sciences Informatics. `,
        v.dataset_doi ? link("https://doi.org/" + v.dataset_doi, "https://doi.org/" + v.dataset_doi) : "DOI not stated"))),
      h("p", { class: "gap" }, "PSI asks users to cite each dataset by its DOI. The page's own computations (scores, counts, bins) are the team's, not NASA's.")) : null);
}

// Compare · Points to consider: one line per need, what the recorded tests say for this environment
// (scenario_needs.csv for the demo scenarios) and what a count means (data's needs.json "reading").
function renderPoints(out, pipe) {
  const box = $("#points");
  box.replaceChildren();
  if (!pipe.needs) return;
  const order = PILLARS.flatMap(([pid]) => pipe.needs.filter((n) => n.pillar === pid));
  const sid = scenarioId(out, pipe);
  const rows = sid && pipe.scenarioNeeds ? pipe.scenarioNeeds.filter((r) => r.scenario_id === sid) : [];
  const spec = sid && pipe.scenarioSpec ? pipe.scenarioSpec.scenarios.find((x) => x.id === sid) : null;
  const ul = h("ul", { class: "points-list" });
  for (const n of order) {
    const r = rows.find((x) => x.need_id === n.id);
    let said = null;
    if (r) {
      const atm = +r.tests_atmosphere || 0, o2o = +r.tests_oxygen_only || 0, po = +r.tests_pressure_only || 0;
      const codes = r.gaps ? r.gaps.split(";").filter(Boolean) : [];
      const parts = [atm ? `${atm} counted tests in the scenario range` : "", o2o ? `${o2o} with oxygen in range and no pressure in the table` : "",
        po ? `${po} with pressure in range and no oxygen in the table` : ""].filter(Boolean);
      said = parts.length ? parts.join("; ") : `no counted test in the scenario range (${(r.status === "other_atmosphere" && otherAtmosphereLabel(codes)) || SN_SHORT[r.status] || r.status})`;
    }
    ul.append(h("li", {}, h("b", {}, n.name), " ",
      said ? [h("span", {}, `— ${spec ? spec.label : "this environment"}: ${said}. `), rowLink("data/pipeline/scenario_needs.csv", r, "row")] : null,
      typeof n.reading === "string" && n.reading ? h("span", { class: "gap reading" }, " What a count means: ", n.reading) : null));
  }
  put(box, h("h3", {}, sid ? `Points to consider for ${spec ? spec.label : sid}` : "Points to consider"),
    sid ? null : h("p", { class: "gap" }, "Counts per environment are computed for the two demo scenarios (ISS, lunar habitat). For other inputs, the table below shows each ranked investigation."),
    ul);
}

// Interpret · Constraints, part 1 of 3 (pm request 1505): what NASA's recorded tests showed, from the
// data role's indicators. Each line carries n_tests and its reading word for word; no criterion and
// no judgement sit next to a value.
const GROUP_WORDS = { material_id: "material", sample_geometry: "shape", fuel_phase: "fuel phase", fuel_material: "fuel", flow_direction: "flow",
  o2_basis: "oxygen basis", source_id: "table" };
function groupWords(g) {
  return String(g || "").split(";").filter(Boolean).map((kv) => { const [k, v] = kv.split("="); return `${GROUP_WORDS[k] || k.replace(/_/g, " ")} ${v}`; }).join(", ");
}
function indicatorValues(ind) {
  const vals = Array.isArray(ind.values) ? ind.values : [];
  const by = (s) => vals.find((v) => v.stat === s && !v.category);
  const cats = vals.filter((v) => v.category);
  const unit = ind.unit ? ` ${ind.unit}` : "";
  if (cats.length) return cats.map((v) => `${v.category} ${v.value}`).join(", ");
  const lo = by("min"), hi = by("max"), med = by("median"), cnt = by("count");
  if (lo && hi) return `${lo.value === hi.value ? lo.value : `${lo.value} to ${hi.value}`}${unit}${med ? `, median ${med.value}` : ""}`;
  if (cnt) return `${cnt.value}${unit}`;
  return vals.map((v) => `${v.stat} ${v.value}`).join(", ") + unit;
}
async function renderShown(out, pipe) {
  const box = $("#shown-body");
  box.replaceChildren();
  const sid = scenarioId(out, pipe);
  const file = sid ? `data/indicators/scenario_${sid}.json` : null;
  if (!file || !OPTIONAL_HAS(file)) {
    box.append(h("p", { class: "gap" }, sid ? "Values from the recorded tests: not available yet."
      : "These values are computed for the two demo scenarios (ISS, lunar habitat). Ask about one of them to see what the recorded tests showed."));
    return;
  }
  pipe.indicators = pipe.indicators || {};
  if (!pipe.indicators[sid]) pipe.indicators[sid] = await loadJSON(file, null);
  const data = pipe.indicators[sid];
  if (!data || !data.needs) { box.append(h("p", { class: "gap" }, "Values from the recorded tests: not available yet.")); return; }
  const spec = pipe.scenarioSpec.scenarios.find((x) => x.id === sid);
  const order = PILLARS.flatMap(([pid]) => (pipe.needs || []).filter((n) => n.pillar === pid));
  for (const n of order) {
    const rows = data.needs[n.id] || [];
    const block = h("div", { class: "shown-need" }, h("h3", {}, `${n.name} `, h("small", {}, `${spec ? spec.label : sid}: ${rows.length} value${rows.length === 1 ? "" : "s"}`)));
    if (!rows.length) block.append(h("p", { class: "gap" }, "No recorded test at this condition gives a value for this need."));
    else block.append(h("ul", { class: "shown-list" }, rows.map((ind) => h("li", {},
      h("b", {}, ind.label || ind.indicator_id), ind.group ? ` (${groupWords(ind.group)})` : "", ": ", indicatorValues(ind),
      " · ", h("b", {}, `${ind.n_tests} test${ind.n_tests === 1 ? "" : "s"}`), " · ",
      ...(ind.investigation_ids || []).flatMap((acc, i) => [i ? ", " : "", link(`https://psi.nasa.gov/physci/repo/data/investigations/${acc}`, acc)]),
      ind.tests_lines ? [" · ", link(`${REPO}data/pipeline/indicator_tests.csv?plain=1#L${ind.tests_lines[0]}-L${ind.tests_lines[1]}`, "tests behind it")] : null,
      Array.isArray(ind.compare_with) && ind.compare_with.length ? h("span", { class: "gap" }, ` A published result exists: ${ind.compare_with.join(", ")}.`) : null,
      ind.reading ? h("span", { class: "gap reading" }, ind.reading) : null))));
    box.append(block);
  }
  box.append(h("p", { class: "gap" }, "Values: ", link(REPO + data.source, data.source), " (indicators, built by the team's data role) and ",
    link(REPO + "data/pipeline/indicator_tests.csv", "data/pipeline/indicator_tests.csv"), " (the tests behind each value)."));
}

// Interpret · Constraints, need by need (data request 1531): the four rungs of data's answer files,
// shown as written. Published entries are quoted, never counted and never drawn as PSI tests.
const KIND = { result: "published result", criterion: "criterion", gap: "stated gap", caveat: "caveat" };
function rowValues(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === "string") return v;
  if (Array.isArray(v)) return v.join("; ");
  return Object.entries(v).map(([k, x]) => `${k.replace(/_/g, " ")} ${x}`).join(", ");
}
function findingItem(e) {
  const rv = e.row ? rowValues(e.row_values) : null;
  const access = e.access && e.access !== "full_text_read" ? ` [${e.access.replace(/_/g, " ")}]` : "";
  return h("li", {}, h("span", { class: "tag" }, KIND[e.kind] || e.kind || "item"), " ",
    e.row ? h("b", {}, `${e.row}: `) : null, rv || e.text || "",
    e.quote && !e.row ? h("q", { class: "quote" }, e.quote) : null,
    h("span", { class: "gap" }, " — ", e.url ? link(e.url, e.title || e.item_id) : (e.title || e.item_id || ""), e.where ? `, ${e.where}` : "", access),
    e.item_note ? h("span", { class: "gap" }, ` Note: ${e.item_note}`) : null);
}
const sentenceList = (arr) => (Array.isArray(arr) && arr.length ? h("ul", { class: "ans-sentences" }, arr.map((s) => h("li", {}, s.text || String(s)))) : null);
const foldList = (title, items, render, open = false) => (Array.isArray(items) && items.length
  ? h("details", { class: "more", open: open ? "" : null }, h("summary", {}, `${title} (${items.length})`), h("ul", { class: "ans-list" }, items.map(render))) : null);
function renderNeedAnswer(doc) {
  const r1 = doc.rung1_recorded_at_the_condition || {}, r2 = doc.rung2_recorded_near_the_condition || {};
  const fr = doc.frame || {}, r3 = doc.rung3_published || {}, r4 = doc.rung4_not_known || {};
  const cells = (r2.cells || []).filter((c) => c.also_matched_at_the_condition === undefined || c.also_matched_at_the_condition !== c.matched);
  const part = (title, ...kids) => h("div", { class: "ans-part" }, h("h4", {}, title), ...kids);
  return h("div", { class: "ans-need" },
    part("What NASA's recorded tests showed",
      sentenceList(r1.sentences),
      foldList("Values from the recorded tests", r1.indicators, (ind) => h("li", {}, h("b", {}, ind.label || ind.id), ind.group ? ` (${groupWords(ind.group)})` : "", ": ",
        indicatorValues(ind), " · ", h("b", {}, `${ind.n_tests} test${ind.n_tests === 1 ? "" : "s"}`), ind.reading ? h("span", { class: "gap reading" }, ind.reading) : null), true),
      sentenceList(r2.sentences),
      cells.length ? h("ul", { class: "ans-list" }, cells.map((c) => h("li", {}, `${c.o2_bin_label} × ${c.pressure_bin_label}`,
        c.differs_in || c.differs ? ` (differs in ${c.differs_in || c.differs})` : "", `: ${c.matched} matched test${c.matched === 1 ? "" : "s"}`))) : null),
    part("Criteria in NASA documents",
      sentenceList(fr.sentences),
      foldList("Criteria, requirements and definitions", fr.criteria, findingItem),
      foldList("Questions and research needs named in NASA documents", fr.nasa_questions, findingItem)),
    part("Published by NASA and the investigators (not in PSI's experimental tables)",
      sentenceList(r3.sentences),
      foldList("At this environment", r3.at_the_environment, findingItem, true),
      foldList("About a stated condition", r3.about_a_stated_condition, findingItem, true),
      foldList("Stated without these conditions", r3.stated_without_these_conditions, findingItem)),
    part("Where the evidence stops for this need",
      sentenceList(r4.sentences),
      Array.isArray(r4.gaps) && r4.gaps.length ? h("ul", { class: "ans-list" }, r4.gaps.map((g) => h("li", {}, g.text || g.code))) : null,
      foldList("Stated as not known in a document", r4.stated_open_elsewhere, findingItem, true),
      foldList("Searches with no result", r4.searches, (s) => h("li", {}, `${s.what}: ${s.result}`, h("span", { class: "gap" }, ` (${[s.where, s.when, s.by].filter(Boolean).join(", ")})`)), true),
      foldList("Areas the PSI tables cannot address", r4.not_covered, (x) => h("li", {}, h("b", {}, x.area), x.why ? `: ${x.why}` : "", x.source_item ? h("span", { class: "gap" }, ` (${x.source_item})`) : null))));
}
async function renderAnswers(out, pipe) {
  const box = $("#answers-body");
  box.replaceChildren();
  const sid = scenarioId(out, pipe);
  const idxFile = sid ? `data/answers/${sid}_index.json` : null;
  const on = Boolean(idxFile && OPTIONAL_HAS(idxFile));
  show("#answers", on); show("#shown", !on); show("#criteria", !on);
  if (!on) return;
  pipe.answersIndex = pipe.answersIndex || {};
  if (!pipe.answersIndex[sid]) pipe.answersIndex[sid] = await loadJSON(idxFile, null);
  const idx = pipe.answersIndex[sid];
  if (!idx) { show("#answers", false); show("#shown", true); show("#criteria", true); return; }
  const spec = pipe.scenarioSpec.scenarios.find((x) => x.id === sid);
  $("#answers-title").textContent = `What is known for ${spec ? spec.label : sid}, need by need`;
  const order = PILLARS.flatMap(([pid]) => (pipe.needs || []).filter((n) => n.pillar === pid));
  for (const n of order) {
    const e = idx[n.id];
    if (!e) continue;
    const body = h("div", {}, h("p", { class: "gap" }, "Loading…"));
    const d = h("details", { class: "more ans" }, h("summary", {}, h("b", {}, n.name), " ", h("span", { class: "ans-top" }, e.top_line)), body);
    d.addEventListener("toggle", async () => {
      if (!d.open || d.dataset.loaded) return;
      d.dataset.loaded = "1";
      try {
        const doc = await loadJSON(e.file);
        body.replaceChildren(renderNeedAnswer(doc), h("p", { class: "gap" }, "Source: ", link(REPO + e.source, e.source), ", written by the team's data role from the PSI tables and the reference list."));
      } catch (err) { body.replaceChildren(h("p", { class: "gap" }, "This need's answer file could not be loaded.")); d.dataset.loaded = ""; }
    });
    box.append(d);
  }
}

// Interpret · Constraints, part 2 of 3: what NASA documents state per need (data's need_references.csv).
// Shown as the documents' statements, never as a verdict on a test or a requirement of this tool.
const ITEM_TYPE = { acceptance_criterion: "acceptance criterion", requirement: "requirement", definition: "definition", published_result: "published result",
  knowledge_gap: "stated knowledge gap", limitation: "stated limitation", framework: "framework", recommendation: "recommendation",
  operational_practice: "operational practice", design_value: "design value", monitoring_range: "monitoring range", exposure_limit: "crew exposure limit" };
function renderCriteria(pipe) {
  const box = $("#criteria-body");
  box.replaceChildren();
  if (!pipe.refs || !pipe.needs) { box.append(h("p", { class: "gap" }, "Criteria: not available yet.")); return; }
  const order = PILLARS.flatMap(([pid]) => pipe.needs.filter((n) => n.pillar === pid));
  for (const n of order) {
    const items = pipe.refs.filter((x) => x.need_id === n.id);
    if (!items.length) continue;
    const kinds = [...new Set(items.map((x) => ITEM_TYPE[x.item_type] || x.item_type))];
    box.append(h("details", { class: "more criteria-need" },
      h("summary", {}, `${n.name}: ${items.length} item${items.length === 1 ? "" : "s"} from NASA documents (${kinds.slice(0, 3).join(", ")}${kinds.length > 3 ? ", …" : ""})`),
      h("ul", { class: "criteria-list" }, items.map((x) => h("li", {},
        h("span", { class: "tag" }, ITEM_TYPE[x.item_type] || x.item_type), " ", x.text, " ",
        h("span", { class: "gap" }, "— ", x.url ? link(x.url, x.title || x.reference_id) : (x.title || x.reference_id), x.where ? `, ${x.where}` : "", x.issuer ? ` (${x.issuer})` : ""),
        x.item_type === "exposure_limit" ? h("span", { class: "gap" }, " A limit for crew breathing cabin air, not for a test duct; this page compares no test with it.") : null)))));
  }
  box.append(h("p", { class: "gap" }, "Wording is the team's transcription; open the document for the full text. Items: ",
    link(REPO + "data/pipeline/need_references.csv", "data/pipeline/need_references.csv"), ", built by the team's data role."));
}

// The answer in two lines, right under the query box, so the first screen shows the result.
function scenarioCoverage(pipe, id) {
  const rows = (pipe.scenarioNeeds || []).filter((r) => r.scenario_id === id);
  const withTests = rows.filter((r) => (+r.tests_atmosphere || 0) + (+r.tests_oxygen_only || 0) + (+r.tests_pressure_only || 0) > 0).length;
  const spec = pipe.scenarioSpec && pipe.scenarioSpec.scenarios.find((x) => x.id === id);
  return { label: (spec && spec.label) || id, withTests, total: rows.length };
}
function renderGlance(out, pipe) {
  const box = $("#glance");
  box.replaceChildren();
  if (out.status !== "ok" || !out.results.length) { box.hidden = true; return; }
  const top = h("p", {}, h("b", {}, "At a glance: "), "closest NASA investigations ",
    ...out.results.flatMap((r, i) => [i ? ", " : "", h("a", { href: "#top" }, r.investigation_id)]),
    ` (team scores ${out.results.map((r) => r.score).join(", ")}).`);
  const sid = scenarioId(out, pipe);
  const cov = sid && pipe.scenarioNeeds ? COMPARE.map(([id]) => scenarioCoverage(pipe, id)).filter((c) => c.total) : [];
  const second = cov.length
    ? h("p", {}, "Needs with counted recorded tests in the scenario range: ", cov.map((c) => `${c.label} ${c.withTests} of ${c.total}`).join(" · "), ". ",
      h("a", { href: "#compare" }, "Compare"), " · ", h("a", { href: "#stops" }, "Where the evidence stops"))
    : h("p", {}, h("a", { href: "#needs" }, "What the recorded tests say"), " · ", h("a", { href: "#stops" }, "Where the evidence stops"));
  box.append(top, second);
  box.hidden = false;
}

let testsIndex = null, testsIndexP = null;
function loadTestsIndex() {
  if (!testsIndexP) testsIndexP = loadText("data/tests.csv").then((text) => {
    testsIndex = new Map(parseRows(text).map((r) => [r.test_id, r]));
    return testsIndex;
  }).catch((e) => { testsIndexP = null; throw e; });
  return testsIndexP;
}
const fullTestsRow = (t) => ({ _line: /^\d+$/.test(t.line || "") ? +t.line : t._line });
function testLink(id) {
  const t = testsIndex && testsIndex.get(id);
  if (t && t.source_file && /^\d+$/.test(t.source_row))
    return link(`${REPO}data/psi/experimental_tables/${encodeURIComponent(t.source_file)}?plain=1#L${t.source_row}`, id);
  if (t) return rowLink("data/pipeline/tests.csv", fullTestsRow(t), id);
  return h("span", {}, id);
}

// The oxygen and pressure these tests were actually recorded at (from tests.csv), so a count
// "in the scenario range" is never read as "at the challenge's exact bound" (data request 1328).
function recordedAt(list) {
  const span = (k, d) => {
    const v = list.map((r) => testsIndex && testsIndex.get(r.test_id)).filter(Boolean).map((t) => parseFloat(t[k])).filter((x) => !Number.isNaN(x));
    if (!v.length) return null;
    const lo = Math.min(...v), hi = Math.max(...v);
    return lo === hi ? lo.toFixed(d) : `${lo.toFixed(d)} to ${hi.toFixed(d)}`;
  };
  const o2 = span("o2_pct", 1), p = span("pressure_kpa", 1);
  if (!o2 && !p) return "";
  return `Recorded values: ${o2 ? o2 + "% O2" : "O2 not in the table"}; ${p ? p + " kPa" : "pressure not in the table"}. `;
}

async function renderTests(out, pipe, cat, phaseFilter) {
  const sec = $("#tests");
  const box = $("#tests-body");
  const sid = scenarioId(out, pipe);
  if (!sid || !pipe.hasScenarioTests) { sec.hidden = true; return; }
  sec.hidden = false;
  box.replaceChildren(h("p", { class: "gap" }, "Loading the test list…"));
  let rows;
  try {
    pipe.scenarioTests = await scenarioTestsOf(pipe);
    await loadTestsIndex();
    rows = pipe.scenarioTests.filter((r) => r.scenario_id === sid);
  } catch (e) { box.replaceChildren(h("p", { class: "gap" }, "Test list: not available yet.")); return; }
  const spec = pipe.scenarioSpec.scenarios.find((x) => x.id === sid);
  const phases = ["all", ...[...new Set(rows.map((r) => r.fuel_phase).filter(Boolean))].sort()];
  const want = phaseFilter || (phases.includes(out.scenario.fuel_phase) ? out.scenario.fuel_phase : "all");
  box.replaceChildren();
  box.append(h("p", { class: "intro" }, h("b", {}, `${spec.label}: `), scenarioRanges(spec), ". ",
    spec.note || "", " ", link(REPO + "pipeline/spec/scenarios.json", "(scenario ranges)")));
  if (spec.caveat) box.append(h("p", { class: "warn" }, spec.caveat));
  const bar = h("div", { class: "presets", role: "group", "aria-label": "Fuel phase" });
  for (const ph of phases) {
    const b = h("button", { type: "button", "aria-pressed": String(ph === want) }, ph === "all" ? "All fuels" : `${ph[0].toUpperCase()}${ph.slice(1)} fuels`);
    b.addEventListener("click", () => renderTests(out, pipe, cat, ph));
    bar.append(b);
  }
  box.append(bar);
  const sel = rows.filter((r) => want === "all" || r.fuel_phase === want);
  const byInv = new Map();
  for (const r of sel) {
    if (r.tier === "other") continue;
    if (!byInv.has(r.investigation_id)) byInv.set(r.investigation_id, { atmosphere: [], oxygen_only: [], pressure_only: [] });
    byInv.get(r.investigation_id)[r.tier].push(r);
  }
  const otherN = sel.filter((r) => r.tier === "other").length;
  const name = (acc) => { const inv = Object.values(cat.investigations).find((v) => v.psi_accession === acc); return inv ? inv.investigation_id : acc; };
  if (!byInv.size) {
    box.append(h("p", { class: "cov-sum is-thin" }, h("b", {}, "No recorded test "), want === "all" ? "" : `with ${want} fuel `,
      `matches these ranges for oxygen or pressure. ${otherN} recorded test${otherN === 1 ? " was" : "s were"} run in other conditions or did not record them.`));
  } else {
    const thead = h("tr", {}, h("th", { scope: "col" }, "Investigation"), ...TIERS.map(([, l, d]) => h("th", { scope: "col", class: "num", title: d }, l)));
    const tb = h("tbody");
    for (const [acc, t] of byInv) {
      const tr = h("tr", {}, h("th", { scope: "row" }, h("b", {}, name(acc)), " ", link(`https://psi.nasa.gov/physci/repo/data/investigations/${acc}`, acc)));
      for (const [tier] of TIERS) {
        const list = t[tier];
        if (!list.length) { tr.append(h("td", { class: "num c-none" }, "0")); continue; }
        const flowIn = list.filter((r) => r.flow_match === "in").length;
        const gravDiff = list.filter((r) => r.gravity_match === "different").length;
        tr.append(h("td", { class: "num" }, h("details", { class: "tests-list" },
          h("summary", {}, `${list.length} test${list.length === 1 ? "" : "s"}`),
          h("p", { class: "gap" }, recordedAt(list)),
          h("p", { class: "gap" }, spec.ranges && spec.ranges.flow_cms ? `${flowIn} with flow in range. ` : "", gravDiff ? `All ${gravDiff} at microgravity, not ${spec.gravity_level} gravity. ` : ""),
          h("p", { class: "ids" }, ...list.flatMap((r, i) => [i ? ", " : "", testLink(r.test_id)])))));
      }
      tb.append(tr);
    }
    box.append(h("div", { class: "table-wrap" }, h("table", { class: "tests-table" }, h("thead", {}, thead), tb)));
    box.append(h("p", { class: "gap" }, `${otherN} more recorded test${otherN === 1 ? "" : "s"} ${want === "all" ? "" : `with ${want} fuel `}were run in other conditions or did not record oxygen and pressure. `,
      "Each test id links to its row in the NASA PSI table. Matching: ", link(REPO + "data/pipeline/scenario_tests.csv", "data/pipeline/scenario_tests.csv"), "."));
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

// ------------------------------------------------------------------ how AI is used here (pm request 1705)
// Reads pm's data/insights/quality.json, model_readiness.json and robustness.json. Every sentence and
// number is printed as the files give it; the page computes nothing here.
const normQuery = (s) => String(s || "").trim().toLowerCase().replace(/\s+/g, " ");
function robustRunFor(rb, q, config) {
  if (!rb || !Array.isArray(rb.runs)) return null;
  const run = rb.runs.find((x) => normQuery(x.query) === normQuery(q));
  // a sampling run of another scoring version describes another ranking: show nothing
  if (!run || (run.config_version && config && config.version && run.config_version !== config.version)) return null;
  return run;
}
function robustLine(run, r) {
  if (!run || !Array.isArray(run.results)) return null;
  const x = run.results.find((e) => e.investigation_id === r.investigation_id);
  return x && typeof x.display_line === "string" && x.display_line ? x.display_line : null;
}
const countTag = () => h("span", { class: "tag" }, "Counted by team code");
function renderAiUse(ai, onQuery) {
  const body = $("#ai-use-body");
  const parts = [];
  const q = ai.quality;
  if (q && typeof q.proposed === "number") {
    const before = q.removed_before_review && typeof q.removed_before_review === "object" ? q.removed_before_review.n : q.removed_before_review;
    const steps = [[q.proposed, "sentences written by the model"], [q.dropped_by_gates, "refused by code checks"],
      [before, "removed by a first reading"], [q.removed_by_review, "removed by the review"], [q.shipped_model_sentences, "shown"]]
      .filter(([n]) => typeof n === "number");
    parts.push(h("div", { class: "ai-part" },
      h("h3", {}, "1. The language model, measured"),
      h("ul", { class: "ai-funnel", "aria-label": "Model-written sentences at each check" }, steps.map(([n, t]) => h("li", {}, h("b", {}, String(n)), " ", t))),
      h("p", {}, `Reviewed by a second AI session: ${q.reviewed_ai_session ?? "not recorded"}. Reviewed by a person: ${q.reviewed_person ?? "not recorded"}.`),
      h("p", {}, "A sentence is shown or not shown; none is reworded. Every shown sentence cites the NASA sentences it rests on."),
      h("p", { class: "gap" }, "Counts: ", link(REPO + "data/insights/quality.json", "data/insights/quality.json"), " ", countTag())));
  }
  const m = ai.readiness;
  if (m && Array.isArray(m.rows) && m.rows.length) {
    parts.push(h("div", { class: "ai-part" },
      h("h3", {}, "2. ", m.title || "Can these NASA tables support an outcome model?"),
      m.labels_and_limits ? h("p", { class: "gap" }, m.labels_and_limits) : null,
      h("ul", { class: "ai-rows" }, m.rows.map((r) => h("li", {}, h("b", {}, r.label), ": ", r.verdict,
        r.baseline && r.model ? h("span", { class: "ai-metric" }, `${r.model.name}: ${r.model.metric} ${r.model.mean}, against ${r.baseline.mean} for the base rate`) : null))),
      m.fixed_line ? h("p", {}, h("b", {}, m.fixed_line)) : null,
      h("p", { class: "gap" }, "Diagnostics: ", link(REPO + "data/insights/model_readiness.json", "data/insights/model_readiness.json"), " ", computedTag())));
  }
  const rb = ai.robust;
  if (rb && Array.isArray(rb.runs) && rb.runs.length) {
    const qs = rb.runs.map((x) => x.query).filter(Boolean);
    parts.push(h("div", { class: "ai-part" },
      h("h3", {}, "3. Does the ranking depend on the team's weights?"),
      rb.label ? h("p", { class: "gap" }, rb.label) : null,
      h("p", {}, "Each result card of these queries shows its line, under \"Weight check\": ",
        ...qs.flatMap((x, i) => [i ? ", " : "", h("a", { href: "?q=" + encodeURIComponent(x), "data-q": x }, x)]), "."),
      h("p", { class: "gap" }, "Sampling: ", link(REPO + "data/insights/robustness.json", "data/insights/robustness.json"), " ", countTag())));
  }
  body.replaceChildren(...parts);
  body.querySelectorAll("a[data-q]").forEach((a) => a.addEventListener("click", (e) => { e.preventDefault(); onQuery(a.dataset.q); }));
  show("#ai-use", parts.length > 0);
}

// ------------------------------------------------------------------ evidence map (pm role, data/insights/evidence_map.json)
// One oxygen axis, three lanes, one dot per group of recorded tests. Every number and label is read
// from the file; the page only draws it and marks the oxygen value the query was read as.
const SVGNS = "http://www.w3.org/2000/svg";
function sv(tag, attrs = {}, ...kids) {
  const el = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined && v !== false) el.setAttribute(k, v);
  for (const kid of kids.flat()) if (kid !== null && kid !== undefined && kid !== false) el.append(typeof kid === "string" ? document.createTextNode(kid) : kid);
  return el;
}
const LANES = [["gas", "Gas flames"], ["liquid", "Fuel droplets"], ["solid", "Solid fuels"]];
function testHref(id) {
  const t = testsIndex && testsIndex.get(id);
  if (t && t.source_file && /^\d+$/.test(t.source_row)) return `${REPO}data/psi/experimental_tables/${encodeURIComponent(t.source_file)}?plain=1#L${t.source_row}`;
  if (t) return `${REPO}data/pipeline/tests.csv?plain=1#L${fullTestsRow(t)._line}`;
  return `${REPO}data/pipeline/tests.csv`;
}
const targetO2 = (t) => (typeof t.o2_pct === "number" ? t.o2_pct : typeof t.o2_min === "number" ? t.o2_min : null);
const BALANCE = { co2_added: "carbon dioxide added", he_added: "helium added", n2_only: "nitrogen balance", not_recorded: "balance gas not recorded" };

async function renderEvidenceMap(out, pipe) {
  const box = $("#stops-map");
  box.replaceChildren();
  const em = pipe.evidenceMap;
  const pts = em && Array.isArray(em.points) ? em.points.filter((p) => typeof p.o2_pct === "number") : [];
  if (!pts.length) { box.append(h("p", { class: "gap" }, "Evidence map: not available yet.")); return; }
  try { await loadTestsIndex(); } catch (e) { /* dot links then point to tests.csv */ }
  const labels = em.labels || {};
  const allTargets = Array.isArray(em.targets) ? em.targets : [];
  // draw: "text" marks (the spacesuit, 95 to 100% oxygen) are given as text, off the axis (pm request 1622).
  const textTargets = allTargets.filter((t) => t.draw === "text");
  const targets = allTargets.filter((t) => t.draw !== "text" && targetO2(t) !== null);
  // By default only the challenge statement and the two demo presets; the rest behind a switch.
  const isPrimary = (t) => t.kind === "challenge_statement" || t.id === "preset.iss" || t.id === "preset.lunar_habitat";
  const flights = Array.isArray(em.flight_tests_not_in_psi) ? em.flight_tests_not_in_psi.filter((t) => typeof t.o2_pct === "number") : [];
  const userO2 = typeof out.scenario.o2_pct === "number" ? out.scenario.o2_pct : null;
  const axisMax = (em.axes && em.axes.o2_pct && em.axes.o2_pct.max) || 45;
  const top = Math.max(axisMax, ...pts.map((p) => p.o2_pct), ...targets.map(targetO2), ...flights.map((t) => t.o2_pct), userO2 || 0);
  const xmax = Math.min(100, Math.ceil(top / 5) * 5 + (top > axisMax ? 5 : 0));
  const W = 760, L = 112, R = 20, T = 44, LH = 62, B = 36, H = T + LANES.length * LH + B;
  const x = (o2) => L + ((W - L - R) * o2) / xmax;
  const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, class: "emap", role: "img",
    "aria-label": `${labels.title || "Evidence map"}: recorded tests by oxygen in three lanes${userO2 !== null ? `, your input at ${userO2}% oxygen` : ""}` });
  const step = xmax > 50 ? 10 : 5;
  for (let v = 0; v <= xmax; v += step) {
    svg.append(sv("line", { x1: x(v), x2: x(v), y1: T, y2: T + LANES.length * LH, class: "emap-grid" }),
      sv("text", { x: x(v), y: T + LANES.length * LH + 16, class: "emap-tick", "text-anchor": "middle" }, `${v}%`));
  }
  svg.append(sv("text", { x: L + (W - L - R) / 2, y: H - 4, class: "emap-axis", "text-anchor": "middle" }, "Oxygen in the surrounding atmosphere, as recorded"));
  const lanePts = {};
  LANES.forEach(([id, name], i) => {
    const y0 = T + i * LH;
    const mine = pts.filter((p) => p.fuel_phase === id);
    lanePts[id] = mine;
    const n = mine.reduce((a, p) => a + (+p.n_tests || 0), 0);
    svg.append(sv("rect", { x: L, y: y0, width: W - L - R, height: LH, class: i % 2 ? "emap-lane alt" : "emap-lane" }),
      sv("text", { x: 6, y: y0 + LH / 2 - 2, class: "emap-lane-name" }, name),
      sv("text", { x: 6, y: y0 + LH / 2 + 14, class: "emap-lane-n" }, `${n} recorded tests`));
    mine.forEach((p, k) => {
      const hollow = p.balance_gas === "co2_added" || p.balance_gas === "he_added";
      const r = Math.min(8, 2.2 + 1.3 * Math.sqrt(+p.n_tests || 1));
      const cy = y0 + 10 + ((k * 37) % (LH - 20));
      const tip = `${p.investigation_id}: ${+p.n_tests || 1} test${+p.n_tests === 1 ? "" : "s"} at ${p.o2_pct}% O2, ${p.pressure_kpa === null || p.pressure_kpa === undefined ? "pressure not recorded" : p.pressure_kpa + " kPa"}, ${BALANCE[p.balance_gas] || p.balance_gas || "balance gas not recorded"}`;
      const first = Array.isArray(p.test_ids) && p.test_ids.length ? p.test_ids[0] : null;
      svg.append(sv("a", { href: first ? testHref(first) : `https://psi.nasa.gov/physci/repo/data/investigations/${p.investigation_id}`, target: "_blank", rel: "noopener" },
        sv("circle", { cx: x(p.o2_pct), cy, r, class: hollow ? "emap-dot hollow" : "emap-dot" }, sv("title", {}, tip))));
    });
    if (id === "solid" && mine.length) {
      const hi = Math.max(...mine.map((p) => p.o2_pct));
      svg.append(sv("line", { x1: x(hi), x2: x(hi), y1: y0 + 4, y2: y0 + LH - 4, class: "emap-end" }),
        sv("text", { x: x(hi) + 6, y: y0 + LH / 2 + 4, class: "emap-end-label" }, `ends at ${hi}%`, sv("title", {}, `Highest recorded oxygen of a solid-fuel test: ${hi}%`)));
    }
  });
  const usedLabelX = [];
  targets.forEach((t, i) => {
    const tx = x(targetO2(t));
    const onYou = userO2 !== null && Math.abs(targetO2(t) - userO2) < 0.5; // keep the number readable beside the input line
    // Marks at the same oxygen (the challenge's 30% and the lunar preset): spread their numbers apart.
    let lx = onYou ? tx - 8 : tx;
    const sameGroup = isPrimary(t);
    while (usedLabelX.some((u) => u.primary === sameGroup && Math.abs(u.x - lx) < 12)) lx -= 14;
    usedLabelX.push({ x: lx, primary: sameGroup });
    svg.append(sv("line", { x1: tx, x2: tx, y1: T - 4, y2: T + LANES.length * LH, class: isPrimary(t) ? "emap-target" : "emap-target secondary" }),
      sv("text", { x: lx, y: T - 7, class: isPrimary(t) ? "emap-target-n" : "emap-target-n secondary", "text-anchor": onYou || lx !== tx ? "end" : "middle" }, String(i + 1)));
  });
  flights.forEach((t) => svg.append(sv("rect", { x: x(t.o2_pct) - 4, y: T + 2 * LH + LH - 14, width: 8, height: 8, class: "emap-flight" },
    sv("title", {}, [`${t.label || "Flight sample from a published paper (not in PSI, not counted)"}: ${t.o2_pct}% O2`,
      typeof t.pressure_kpa === "number" ? `, ${t.pressure_kpa} kPa` : "", t.what ? `. ${t.what}` : ""].join("")))));
  if (userO2 !== null) {
    const ux = x(Math.min(userO2, xmax));
    svg.append(sv("line", { x1: ux, x2: ux, y1: 6, y2: T + LANES.length * LH, class: "emap-you" }),
      sv("text", { x: ux + (ux > W - 150 ? -6 : 6), y: 16, class: "emap-you-label", "text-anchor": ux > W - 150 ? "end" : "start" }, `your input: ${userO2}% O2`));
  }

  const head = h("p", { class: "emap-title" }, h("b", {}, labels.title || "Where the PSI test tables stop"), " ", computedTag());
  const counts = h("ul", { class: "emap-counts" });
  for (const [id, name] of LANES) {
    const mine = lanePts[id] || [];
    const total = mine.reduce((a, p) => a + (+p.n_tests || 0), 0);
    const li = h("li", {}, h("b", {}, `${name}: `));
    if (userO2 !== null) {
      const at = mine.filter((p) => p.o2_pct >= userO2);
      const n = at.reduce((a, p) => a + (+p.n_tests || 0), 0);
      const byInv = new Map();
      for (const p of at) { const e = byInv.get(p.investigation_id) || { n: 0, id: null }; e.n += +p.n_tests || 0; e.id = e.id || (p.test_ids || [])[0]; byInv.set(p.investigation_id, e); }
      li.append(`${n} of ${total} recorded tests at or above ${userO2}% oxygen`,
        ...(byInv.size ? [" (", ...[...byInv].flatMap(([inv, e], i) => [i ? ", " : "", link(e.id ? testHref(e.id) : `https://psi.nasa.gov/physci/repo/data/investigations/${inv}`, `${inv} ${e.n}`)]), ")"] : []), ".");
    } else li.append(`${total} recorded tests.`);
    const note = labels.lane_notes && labels.lane_notes[id];
    if (note) li.append(" ", h("span", { class: "gap" }, note[0].toUpperCase() + note.slice(1) + "."));
    counts.append(li);
  }
  const marks = targets.length ? h("ol", { class: "emap-targets" }, targets.map((t) =>
    h("li", { class: isPrimary(t) ? null : "secondary-item" }, t.label || t.id, " ", h("span", { class: "gap" }, `(${String(t.kind || "").replace(/_/g, " ")}; ${t.source || "source not given"}${t.access ? ", " + t.access : ""}). A mark, not a limit.`),
      isPrimary(t) ? null : h("span", { class: "gap" }, " Drawn when cited atmospheres are shown.")))) : null;
  const textMarks = textTargets.length ? h("p", { class: "gap" }, "Given as text, off the oxygen axis: ", textTargets.map((t) => t.label || t.id).join("; "), ".") : null;
  const toggle = targets.some((t) => !isPrimary(t)) ? (() => {
    const cb = h("input", { type: "checkbox", id: "emap-cited" });
    cb.addEventListener("change", () => wrap.classList.toggle("show-secondary", cb.checked));
    return h("label", { class: "emap-toggle", for: "emap-cited" }, cb, " Show cited atmospheres and the team's counting ranges (", String(targets.filter((t) => !isPrimary(t)).length), " more marks)");
  })() : null;
  const np = em.not_plotted || {};
  const missing = [];
  if (np.oxidizer_stream && np.oxidizer_stream.n) missing.push(`${np.oxidizer_stream.n} tests whose oxygen value is a burner's oxidizer stream${np.oxidizer_stream.why ? ": " + np.oxidizer_stream.why : ""}`);
  if (np.no_ambient_oxygen_value && np.no_ambient_oxygen_value.n) missing.push(`${np.no_ambient_oxygen_value.n} tests with no surrounding-atmosphere oxygen value${np.no_ambient_oxygen_value.rule ? ": " + np.no_ambient_oxygen_value.rule : ""}`);
  if (np.psi20_test_day_table && np.psi20_test_day_table.days) missing.push(`ACME-BRE (PSI-20): a test-day table (${np.psi20_test_day_table.days} days${np.psi20_test_day_table.flames_ignited ? ", " + np.psi20_test_day_table.flames_ignited + " flames ignited" : ""}), not single tests`);
  const wrap = h("div", { class: "emap-wrap" }, svg);
  box.append(...[head,
    userO2 === null ? h("p", { class: "warn" }, "Your input has no oxygen value, so it is not marked. Add one, for example 30% O2.") : null,
    wrap,
    h("p", { class: "gap emap-legend" }, "Filled dot: tests in nitrogen balance or balance not recorded. Hollow dot: carbon dioxide or helium added. Dot size grows with the number of tests. Each dot links to its row in the NASA table.",
      flights.length ? " Small squares: " + (labels.saffire_note && !(labels.caption || []).join(" ").includes(labels.saffire_note)
        ? labels.saffire_note : `${flights[0].label || "flight samples from a published paper (not in PSI, not counted)"}; see the note below the list.`) : ""),
    toggle, counts, marks, textMarks,
    missing.length ? h("p", { class: "gap" }, "Not in the picture: ", missing.join("; "), ".") : null,
    Array.isArray(labels.caption) && labels.caption.length ? h("p", { class: "gap" }, labels.caption.join(" ")) : null,
    h("p", { class: "gap" }, "Points: ", link(REPO + "data/insights/evidence_map.json", "data/insights/evidence_map.json"), ", built by team code from ",
      link(REPO + "data/pipeline/tests.csv", "data/pipeline/tests.csv"), ".")].filter(Boolean));
  // On a narrow screen the picture scrolls inside its box: start with the input's marker in view.
  if (userO2 !== null && wrap.scrollWidth > wrap.clientWidth) {
    const frac = x(Math.min(userO2, xmax)) / W;
    wrap.scrollLeft = Math.max(0, frac * wrap.scrollWidth - wrap.clientWidth / 2);
  }
}

function show(id, on) { $(id).hidden = !on; }
function setStatus(text, kind) {
  const s = $("#status");
  s.className = "status" + (kind ? " is-" + kind : "");
  s.textContent = text || "";
}

// web/build.py writes the build commit here, so every data file is fetched as file?v=<commit>:
// a new deploy is read at once, and a page never mixes files from two builds (Pages caches 10 min).
const DATA_V = "__BUILD__";
let OPTIONAL_HAS = () => true; // set in main() from build.json
const vurl = (p) => (DATA_V.startsWith("__") ? p : `${p}${p.includes("?") ? "&" : "?"}v=${DATA_V}`);
async function loadJSON(path, fallback) {
  try { const r = await fetch(vurl(path)); if (!r.ok) throw new Error(r.status); return await r.json(); }
  catch (e) { if (fallback !== undefined) return fallback; throw e; }
}
async function loadText(path) { const r = await fetch(vurl(path)); if (!r.ok) throw new Error(`${path}: ${r.status}`); return r.text(); }

async function main() {
  setStatus("Loading the catalog and the NASA test tables…");
  let config, scorer, invOrder = [], insights = { cards: {} };
  // build.json lists the optional files this build has; others are not fetched (no 404s).
  const build = await loadJSON("data/build.json", null);
  const has = (p) => !build || !Array.isArray(build.optional) || build.optional.includes(p);
  const optJSON = (p, fb) => (has(p) ? loadJSON(p, fb) : Promise.resolve(fb));
  OPTIONAL_HAS = has;
  try {
    const [cfg, invCsv, cfgCsv, cards] = await Promise.all([
      loadJSON("data/scoring_config.json"), loadText("data/investigations.csv"), loadText("data/configurations.csv"),
      optJSON("data/insights/cards.json", null)]);
    insights.scenarios = await optJSON("data/insights/scenarios.json", []);
    insights.raw = await optJSON("data/raw_inventory_sentences.json", null);
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
  // The loading line stays until the first result is drawn (run() clears it).
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
  const [sn, ss, stHead] = await Promise.all([
    OPTIONAL_HAS("data/scenario_needs.csv") ? optText("data/scenario_needs.csv") : null,
    OPTIONAL_HAS("data/scenario_spec.json") ? loadJSON("data/scenario_spec.json", null) : null,
    OPTIONAL_HAS("data/scenario_tests.csv") ? fetch(vurl("data/scenario_tests.csv"), { method: "HEAD" }).then((r) => r.ok).catch(() => false) : false]);
  pipe.scenarioNeeds = sn ? parseRows(sn) : null;
  pipe.evidenceMap = OPTIONAL_HAS("data/insights/evidence_map.json") ? await loadJSON("data/insights/evidence_map.json", null) : null;
  const [aiQuality, aiReadiness, aiRobust] = await Promise.all([optJSON("data/insights/quality.json", null),
    optJSON("data/insights/model_readiness.json", null), optJSON("data/insights/robustness.json", null)]);
  pipe.scenarioSpec = ss && Array.isArray(ss.scenarios) ? ss : null;
  pipe.hasScenarioTests = Boolean(stHead && pipe.scenarioSpec);
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
      show("#top", false); show("#all", false); show("#needs", false); show("#stops", false); show("#gaps-section", false); show("#tests", false); show("#glance", false); show("#criteria", false); show("#shown", false); show("#answers", false);
      $("#assumptions").replaceChildren();
      setStatus(out.status === "out_of_scope" ? "Out of scope for this tool." : "Add an environment or a material to start.", "info");
      return;
    }
    setStatus("");
    const sc = scenarioNotes(q, out, insights);
    insights.robustRun = robustRunFor(aiRobust, q, config);
    renderResults(out, cat, insights, sc);
    renderScenarioText(out, sc, cat);
    renderRanking(out);
    renderGlance(out, pipe);
    renderPoints(out, pipe);
    renderCriteria(pipe);
    renderShown(out, pipe);
    renderExport(out, pipe, cat);
    renderAnswers(out, pipe);
    renderCompare(out, pipe, (q2) => { run(q2); $("#needs").scrollIntoView({ behavior: "smooth", block: "start" }); });
    renderNeeds(out, pipe, false);
    renderCoverage(out, pipe);
    renderTests(out, pipe, cat);
    renderEvidenceMap(out, pipe);
    show("#top", true); show("#all", true); show("#needs", true); show("#stops", true); // #answers, #shown and #criteria are set by renderAnswers()
  }

  renderAiUse({ quality: aiQuality, readiness: aiReadiness, robust: aiRobust }, (q2) => { run(q2); $("#top").scrollIntoView({ behavior: "smooth", block: "start" }); });
  $("#ask-form").addEventListener("submit", (e) => { e.preventDefault(); run($("#q").value.trim()); });
  // "How the score works" links open the folded method text.
  document.querySelectorAll('a[href="#method"]').forEach((a) => a.addEventListener("click", () => { const d = $("#method details"); if (d) d.open = true; }));
  document.querySelectorAll(".presets button").forEach((b) => b.addEventListener("click", () => run(b.dataset.q)));
  const q0 = new URL(location.href).searchParams.get("q");
  run(q0 !== null ? q0 : "ISS", q0 !== null);
}

main();
