// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14). Dashboard: runs the team's ranking in the
// browser (web/scorer.js, checked against scoring/scorer.py) and renders the result.
import { createScorer, parseCSV } from "./scorer.js";

const REPO = "https://github.com/choidol0208/NASA_RAPID/blob/main/";
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

function renderResults(out, cat, insights) {
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
      card ? h("p", {}, h("b", {}, "Summary: "), card.summary, " ", h("span", { class: "tag is-ai" }, card.reviewed_by ? `AI-generated, reviewed by ${card.reviewed_by}` : "AI-generated, not reviewed yet"))
        : h("p", { class: "gap" }, "Written summary: not available yet."),
      r.other_configs.length ? h("p", { class: "gap" }, "Other configurations in this investigation: ", r.other_configs.join(", ")) : null);
    ol.append(h("li", { class: "result" }, head, ...body, warns, tags, links, more));
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
    const [cfg, invCsv, cfgCsv, cards] = await Promise.all([
      loadJSON("data/scoring_config.json"), loadText("data/investigations.csv"), loadText("data/configurations.csv"),
      loadJSON("data/insights/cards.json", null)]);
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
      show("#top", false); show("#all", false);
      $("#assumptions").replaceChildren();
      setStatus(out.status === "out_of_scope" ? "Out of scope for this tool." : "Add an environment or a material to start.", "info");
      return;
    }
    setStatus("");
    renderResults(out, cat, insights);
    renderRanking(out);
    show("#top", true); show("#all", true);
  }

  $("#ask-form").addEventListener("submit", (e) => { e.preventDefault(); run($("#q").value.trim()); });
  document.querySelectorAll(".presets button").forEach((b) => b.addEventListener("click", () => run(b.dataset.q)));
  const q0 = new URL(location.href).searchParams.get("q");
  run(q0 !== null ? q0 : "ISS", q0 !== null);
}

main();
