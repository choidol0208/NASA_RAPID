// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
// Takes the deck's captures of the team's own page (docs/submission/deck/img/) from a local copy of the
// static build, with headless Google Chrome driven over the Chrome DevTools Protocol (Node's built-in
// WebSocket and fetch; no library).
//
// Usage (refresh.sh does all of this):
//   node docs/submission/deck/capture.mjs <site_base_url> [out_dir]
//   node docs/submission/deck/capture.mjs --probe <url> <js expression>
// The site must be served on 127.0.0.1 (a build of web/build.py made in a scratch copy, never web/dist).
// Environment: DECK_ONLY=top.png,cotton_top3.png takes only those captures and keeps the other entries of
// img/captures.json; DECK_CDP_PORT (default 8829); DECK_CHROME_PROFILE; CHROME (path of the browser).
//
// Network: Chrome is started with every host name unresolvable except 127.0.0.1 and the two hosts of the
// page's own web fonts (fonts.googleapis.com, fonts.gstatic.com), which web/index.html loads in its <head>.
// A capture is refused when the page's two font families (Atkinson Hyperlegible, Barlow Semi Condensed)
// did not load, so that no capture shows the system font.
// Viewport 1440 CSS px wide, device scale factor 2, light colour scheme.
import { spawn, execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";

// ------------------------------------------------------------------ what a person may change
// The worked example of slide 3 (docs/submission/slides_outline.md); every query capture uses it.
const QUERY = "lunar habitat cotton fabric";
// The recorded assistant answer shown on slide 6. Taken only when ai/assistant/_runtime/RECORDED_READY
// exists (the new recording is finished). Choose a turn whose answer is written by the model and carries
// citation numbers; the capture's "check" records the label, the citations and the gate line it found.
// Chosen on 15 November 2026 from data/insights/assistant_recorded.json (written 16:36 KST): conversation
// "where_data_iss", turn 2, "Which raw files belong to test FLEX-1?": both sentences of the answer are written
// by the model and kept by the gates, each with the numbers of the facts it cites.
const RECORDED_CONVERSATION = "clarify_first";   // id of the conversation in assistant/recorded.json
const RECORDED_TURN = 2;                          // turn of that conversation, counted from 1

const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const CDP_PORT = Number(process.env.DECK_CDP_PORT || 8829);
const WIDTH = 1440, HEIGHT = 900, SCALE = 2;
const FONT_HOSTS = ["fonts.googleapis.com", "fonts.gstatic.com"];
const PAGE_FONTS = ["Atkinson Hyperlegible", "Barlow Semi Condensed"];
const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, "..", "..", "..");
const PROFILE = process.env.DECK_CHROME_PROFILE || join(tmpdir(), "deck-capture-chrome-profile");

const args = process.argv.slice(2);
const PROBE = args[0] === "--probe";
const BASE = PROBE ? null : (args[0] || "").replace(/\/?$/, "/");
const OUT = PROBE ? null : (args[1] || join(HERE, "img"));
if (!PROBE && !/^http:\/\/127\.0\.0\.1:\d+\/$/.test(BASE)) {
  console.error("usage: node capture.mjs http://127.0.0.1:<port>/ [out_dir]   (the site must be served on 127.0.0.1)");
  process.exit(2);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ------------------------------------------------------------------ Chrome and CDP
rmSync(PROFILE, { recursive: true, force: true });
const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${CDP_PORT}`, "--remote-debugging-address=127.0.0.1",
  `--user-data-dir=${PROFILE}`, "--no-first-run", "--no-default-browser-check", "--disable-extensions",
  "--disable-background-networking", "--disable-component-update", "--disable-sync", "--metrics-recording-only",
  "--disable-features=OptimizationHints,MediaRouter,Translate", "--hide-scrollbars", "--mute-audio",
  `--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1, ${FONT_HOSTS.map((h) => "EXCLUDE " + h).join(", ")}`, "about:blank",
], { stdio: ["ignore", "ignore", "pipe"] });
let chromeErr = "";
chrome.stderr.on("data", (d) => { chromeErr += d; });
const stop = () => { try { chrome.kill(); } catch { /* already gone */ } try { rmSync(PROFILE, { recursive: true, force: true }); } catch { /* Chrome is still closing its files */ } };
process.on("exit", stop);
process.on("SIGINT", () => process.exit(130));
process.on("SIGTERM", () => process.exit(143));

async function cdpReady() {
  for (let i = 0; i < 100; i++) {
    try { const r = await fetch(`http://127.0.0.1:${CDP_PORT}/json/version`); if (r.ok) return r.json(); } catch { /* not yet */ }
    await sleep(150);
  }
  throw new Error("Chrome did not open its debugging port\n" + chromeErr);
}

class Page {
  constructor(ws) { this.ws = ws; this.id = 0; this.wait = new Map(); this.events = []; }
  static async open() {
    const t = await (await fetch(`http://127.0.0.1:${CDP_PORT}/json/new?about:blank`, { method: "PUT" })).json();
    const ws = new WebSocket(t.webSocketDebuggerUrl);
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
    const p = new Page(ws);
    p.targetId = t.id;
    ws.onmessage = (m) => {
      const msg = JSON.parse(m.data);
      if (msg.id && p.wait.has(msg.id)) {
        const { res, rej } = p.wait.get(msg.id); p.wait.delete(msg.id);
        if (msg.error) rej(new Error(JSON.stringify(msg.error))); else res(msg.result);
      } else if (msg.method) p.events.push(msg);
    };
    await p.send("Page.enable");
    await p.send("Runtime.enable");
    await p.send("Network.enable");
    await p.send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: HEIGHT, deviceScaleFactor: SCALE, mobile: false });
    await p.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
    return p;
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((res, rej) => this.wait.set(id, { res, rej }));
  }
  async eval(expr) {
    const r = await this.send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true });
    if (r.exceptionDetails) throw new Error("page error: " + JSON.stringify(r.exceptionDetails).slice(0, 600));
    return r.result.value;
  }
  async until(expr, ms = 30000) {
    const t0 = Date.now();
    while (Date.now() - t0 < ms) { if (await this.eval(expr)) return; await sleep(150); }
    throw new Error("timed out waiting for " + expr);
  }
  async goto(url) {
    await this.send("Page.navigate", { url });
    await this.until("document.readyState === 'complete'");
  }
  async close() { this.ws.close(); await fetch(`http://127.0.0.1:${CDP_PORT}/json/close/${this.targetId}`); }
  consoleErrors() {
    return this.events.filter((e) => (e.method === "Runtime.exceptionThrown") ||
      (e.method === "Runtime.consoleAPICalled" && e.params.type === "error"))
      .map((e) => JSON.stringify(e.params).slice(0, 300));
  }
  // Hosts the page asked for, other than the local site: must be the two font hosts only.
  outsideHosts() {
    const hosts = new Set();
    for (const e of this.events) {
      if (e.method !== "Network.requestWillBeSent") continue;
      try { const u = new URL(e.params.request.url); if (/^https?:$/.test(u.protocol) && u.hostname !== "127.0.0.1") hosts.add(u.hostname); } catch { /* data: and the like */ }
    }
    return [...hosts].sort();
  }
}

// The font families of the page that are loaded now (document.fonts), after waiting for pending loads.
const FONTS_LOADED = `(async () => { await document.fonts.ready;
  return [...new Set([...document.fonts].filter((f) => f.status === "loaded").map((f) => f.family.replace(/["']/g, "")))].sort(); })()`;

async function openUrl(page, url) {
  await page.goto(url);
  if (/[?&]q=/.test(url)) await page.until("document.querySelector('#glance') && !document.querySelector('#glance').hidden");
  else await page.until("document.querySelector('#status') && !/Loading/.test(document.querySelector('#status').textContent)", 30000).catch(() => {});
  await sleep(1200);
  await page.eval(FONTS_LOADED);
}

// The union of the given elements' boxes, in document CSS px, padded and clamped to the page width.
const UNION = `(sels, pad, padY) => {
  const rs = sels.map((s) => document.querySelector(s)).filter((e) => e && !e.closest("[hidden]"))
    .map((e) => e.getBoundingClientRect()).filter((r) => r.height > 0);
  if (!rs.length) return null;
  const sy = window.scrollY, cw = document.documentElement.clientWidth;
  const x0 = Math.max(0, Math.min(...rs.map((r) => r.left)) - pad), x1 = Math.min(cw, Math.max(...rs.map((r) => r.right)) + pad);
  const y0 = Math.max(0, Math.min(...rs.map((r) => r.top)) + sy - padY), y1 = Math.max(...rs.map((r) => r.bottom)) + sy + padY;
  return { x: Math.floor(x0), y: Math.floor(y0), width: Math.ceil(x1 - x0), height: Math.ceil(y1 - y0) };
}`;
// Named boxes inside the clip (CSS px, relative to the clip's top left corner): build_deck.py crops by these names.
const BOXES = `(named, clip) => { const out = {}; const sy = window.scrollY;
  for (const [k, s] of Object.entries(named)) { const e = document.querySelector(s); if (!e) continue; const r = e.getBoundingClientRect(); if (!r.height) continue;
    out[k] = { x: Math.round((r.left - clip.x) * 10) / 10, y: Math.round((r.top + sy - clip.y) * 10) / 10, width: Math.round(r.width * 10) / 10, height: Math.round(r.height * 10) / 10 }; }
  return out; }`;

// ------------------------------------------------------------------ probe mode
const version = await cdpReady();
if (PROBE) {
  const page = await Page.open();
  try {
    await openUrl(page, args[1]);
    console.log(JSON.stringify(await page.eval(args[2]), null, 1));
    const errs = page.consoleErrors();
    if (errs.length) console.log("console errors:", errs.join("\n"));
    console.log("outside hosts:", page.outsideHosts().join(", ") || "none");
  } finally { await page.close(); }
  process.exit(0);
}

// ------------------------------------------------------------------ the captures
mkdirSync(OUT, { recursive: true });
let commit = "unknown";
try { commit = execFileSync("git", ["rev-parse", "--short", "HEAD"], { cwd: REPO }).toString().trim(); } catch { /* not a git checkout */ }
const site = {};
try { site.scoring_config = (await (await fetch(BASE + "data/scoring_config.json")).json()).version; } catch { site.scoring_config = null; }
try { const b = await (await fetch(BASE + "data/build.json")).json(); site.built_at = b.built_at; site.build_commit = b.commit; } catch { /* no build stamp */ }
if (!site.scoring_config) { console.error("capture.mjs: the site gives no data/scoring_config.json with a version; is it a build of web/build.py?"); process.exit(1); }

const manifest = [];
const notTaken = [];

async function capture(spec) {
  const page = await Page.open();
  const url = BASE + (spec.path || "");
  try {
    if (spec.width) await page.send("Emulation.setDeviceMetricsOverride", { width: spec.width, height: HEIGHT, deviceScaleFactor: SCALE, mobile: false });
    await openUrl(page, url);
    if (spec.prepare) { await page.eval(`(async () => { ${spec.prepare} })()`); await sleep(spec.settle || 1200); }
    const fonts = await page.eval(FONTS_LOADED);
    const missing = PAGE_FONTS.filter((f) => !fonts.includes(f));
    if (missing.length) throw new Error(`${spec.file}: the page's font ${missing.join(" and ")} did not load (is the network reachable for ${FONT_HOSTS.join(", ")}?). No capture is written with the system font.`);
    const outside = page.outsideHosts();
    const stray = outside.filter((h) => !FONT_HOSTS.includes(h));
    if (stray.length) throw new Error(`${spec.file}: the page asked for a host other than its font hosts: ${stray.join(", ")}`);
    const clip = await page.eval(`(${UNION})(${JSON.stringify(spec.selectors)}, ${spec.pad ?? 14}, ${spec.padY ?? spec.pad ?? 14})`);
    if (!clip) throw new Error(`${spec.file}: none of ${spec.selectors.join(", ")} is on the page`);
    const boxes = spec.boxes ? await page.eval(`(${BOXES})(${JSON.stringify(spec.boxes)}, ${JSON.stringify(clip)})`) : {};
    const lost = Object.keys(spec.boxes || {}).filter((k) => !boxes[k]);
    if (lost.length) throw new Error(`${spec.file}: the page has no element for the box ${lost.join(", ")}`);
    const check = spec.check ? await page.eval(spec.check) : null;
    const r = await page.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { ...clip, scale: 1 } });
    const png = Buffer.from(r.data, "base64");
    writeFileSync(join(OUT, spec.file), png);
    const errs = page.consoleErrors();
    manifest.push({
      file: spec.file, on_slide: spec.slide ?? null, shows: spec.shows, url, selectors: spec.selectors, prepared: spec.preparedNote || null,
      clip_css_px: clip, pixel_size: { width: clip.width * SCALE, height: clip.height * SCALE }, boxes_css_px: boxes,
      viewport: { width: spec.width || WIDTH, height: HEIGHT, device_scale_factor: SCALE },
      taken_at: new Date().toISOString(), scoring_config: site.scoring_config, page_built_at: site.built_at || null,
      fonts_loaded: fonts, outside_hosts: outside, sha256: createHash("sha256").update(png).digest("hex"), check,
      console_errors: errs.length ? errs : undefined,
      "AI-generated": false, note: "capture of the team's own page",
    });
    console.log("wrote", spec.file, `${clip.width * SCALE}x${clip.height * SCALE}`, "fonts:", fonts.join(" + "));
  } finally { await page.close(); }
}

const Q = "?q=" + encodeURIComponent(QUERY);
const HIDE = (sels) => `${JSON.stringify(sels)}.forEach((s) => document.querySelectorAll(s).forEach((e) => { e.style.display = "none"; }));`;
const CARD = (n) => `#results > li:nth-child(${n})`;
// One question block of a list of <details>, opened alone: the block whose summary starts with the given words.
const OPEN_ONE = (list, words, id) => `const ds = [...document.querySelectorAll(${JSON.stringify(list)})];
  const d = ds.find((x) => x.querySelector("summary").textContent.trim().startsWith(${JSON.stringify(words)}));
  if (!d) throw new Error("no block starts with " + ${JSON.stringify(words)});
  ds.forEach((x) => { x.open = x === d; }); d.id = ${JSON.stringify(id)}; window.scrollTo(0, 0);`;

const specs = [
  {
    file: "top.png", slide: 1, path: "",
    shows: "The start page before a query: the app bar (product name, 'Copy link', 'How it works', 'Source code'), the title and description, the notice line, the question 'What are you building, and where?' with its input and example buttons, and the three cards Find, Compare, Interpret.",
    selectors: ["#appbar", "header.masthead", "main > section.ask", "main > section.verbs"], pad: 0, padY: 0,
    prepare: `const c = document.querySelector("header.masthead p.challenge"); if (c) c.style.display = "none"; window.scrollTo(0, 0);`,
    preparedNote: "The masthead line that quotes the challenge statement (p.challenge) is hidden for this capture only; nothing else is changed.",
    boxes: { appbar: "#appbar", masthead: "header.masthead", eyebrow: "header.masthead .eyebrow", ask: "main > section.ask", verbs: "main > section.verbs" },
    check: `({ challengeLineShown: getComputedStyle(document.querySelector("header.masthead p.challenge")).display !== "none", examples: [...document.querySelectorAll(".presets button")].map((b) => b.textContent.trim()), input: document.querySelector("#q").value, appbar: document.querySelector("#appbar").innerText.replace(/\\s+/g, " ").trim(), verbs: document.querySelector("main > section.verbs").innerText.replace(/\\s+/g, " ").trim() })`,
  },
  {
    file: "cotton_top3.png", slide: 3, path: Q + "&tab=closest",
    shows: `Tab 'Closest investigations' for '${QUERY}': the section heading with the note that scores and order are the team's computation, then the three result cards whole, in the page's compact form (rank, name, team score, closest configuration, dimension strip, 'Why', 'Largest gap', cautions, tags; 'Details and sources' closed).`,
    selectors: ["#top .kicker", "#top .section-head", CARD(1), CARD(2), CARD(3)],
    boxes: { head: "#top .section-head", card1: CARD(1), card2: CARD(2), card3: CARD(3),
      gap1: CARD(1) + " .gap", gap2: CARD(2) + " .gap", gap3: CARD(3) + " .gap",
      strip1: CARD(1) + " .strip", strip2: CARD(2) + " .strip", strip3: CARD(3) + " .strip" },
    check: `[...document.querySelectorAll("#results > li")].slice(0, 3).map((li) => ({ rank: li.querySelector(".rank").textContent.trim(), name: li.querySelector("h3").textContent.trim(), score: li.querySelector(".score").innerText.replace(/\\s+/g, " ").trim(), why: (li.querySelector(".why") || {}).textContent, gap: (li.querySelector(".gap") || {}).textContent, tags: [...li.querySelectorAll(".tags > *")].map((t) => t.textContent.trim()), details_open: [...li.querySelectorAll("details.card-more")].map((d) => d.open), note: document.querySelector("#top .section-head").innerText.replace(/\\s+/g, " ").trim() }))`,
  },
  {
    file: "cotton_glance.png", slide: null, path: Q + "&tab=closest",
    shows: `The summary tiles ('At a glance') for '${QUERY}': the three closest investigations with their team scores, the count of questions with recorded tests in range, and the raw-data line.`,
    selectors: ["#glance"],
    check: `document.querySelector("#glance").innerText.replace(/\\s+/g, " ").trim()`,
  },
  {
    file: "cotton_read.png", slide: null, path: Q + "&tab=closest",
    shows: `Block 'How your input was read' for '${QUERY}': its heading and the chips (environment, oxygen, pressure, airflow, gravity, material, material type, fuel phase, burning behaviour, thickness, shape, question), each with where the value came from.`,
    selectors: ["#read-title", "#conditions"],
    preparedNote: "Only the heading and the chips are captured; the block 'Filled in for you, not typed' (#assumptions), which quotes a section title of the challenge statement, is outside the capture.",
    check: `[...document.querySelectorAll("#conditions > li")].map((li) => li.textContent.trim().replace(/\\s+/g, " "))`,
  },
  {
    file: "lunar_found.png", slide: 4, path: Q + "&tab=found",
    shows: `Tab 'What was found' for '${QUERY}' (the lunar-habitat environment), its first section 'What NASA's experiments and documents report, question by question': heading and note, then the block 'Flame spread and growth' open with its headline of counts and its first three quoted results (group, quotation, source, printed values).`,
    selectors: ["#results-first .kicker", "#results-first .section-head", "#cap-p3"], padY: 2,
    prepare: OPEN_ONE("#results-first-body > details.rf-need", "Flame spread", "cap-p3"),
    preparedNote: "The block 'Flame spread and growth (P3)' is open and the other question blocks are closed; 'Show all' inside it is left closed, as on the page.",
    boxes: { head: "#results-first .section-head", block: "#cap-p3", summary: "#cap-p3 > summary", headline: "#cap-p3 .rf-headline",
      item1: "#cap-p3 .rf-list > li:nth-child(1)", item2: "#cap-p3 .rf-list > li:nth-child(2)", item3: "#cap-p3 .rf-list > li:nth-child(3)" },
    check: `({ head: document.querySelector("#results-first .section-head").innerText.replace(/\\s+/g, " ").trim(), headline: document.querySelector("#cap-p3 .rf-headline").innerText, items: [...document.querySelectorAll("#cap-p3 > .rf-list > li")].map((li) => ({ group: (li.querySelector(".rf-group") || {}).textContent, quote: (li.querySelector(".rf-quote") || {}).textContent, source: (li.querySelector(".rf-src") || {}).innerText, relation: (li.querySelector(".rf-rel") || {}).textContent, values: (li.querySelector(".rf-values") || {}).textContent })) })`,
  },
  {
    file: "lunar_evidence_map.png", slide: 7, path: Q + "&tab=stops",
    shows: `Tab 'Where the evidence stops' for '${QUERY}': heading and note, the evidence map (recorded tests on the oxygen axis by kind of fuel, the input marked) and its legend.`,
    selectors: ["#stops .kicker", "#stops .section-head", "#stops-map .emap-title", "#stops-map .emap-wrap", "#stops-map .emap-legend"], padY: 4,
    boxes: { head: "#stops .section-head", title: "#stops-map .emap-title", map: "#stops-map .emap-wrap", legend: "#stops-map .emap-legend" },
    check: `(() => { const w = document.querySelector("#stops-map .emap-wrap"); return { title: (document.querySelector("#stops-map .emap-title") || {}).innerText, text: w.innerText.slice(0, 800), scrollW: w.scrollWidth, clientW: w.clientWidth }; })()`,
  },
];

// The three piles (tab 'Where the data are'): filled in below, once the section's blocks are known.
const PILES = (file, words, id, slide, what) => ({
  file, slide, path: Q + "&tab=data",
  shows: `Tab 'Where the data are' for '${QUERY}' (the lunar-habitat environment), section 'Where the data are: in NASA's tables, in the archive, or no record': the block '${words}' open with its three piles (${what}).`,
  selectors: ["#" + id], padY: 4,
  prepare: OPEN_ONE("#piles-body > details.pile-need", words, id),
  preparedNote: `The block '${words}' is open and the other question blocks are closed; folds inside it are left as on the page.`,
  boxes: { block: "#" + id, summary: `#${id} > summary`, pile1: `#${id} > .pile:nth-of-type(1)`, pile1_first: `#${id} > .pile:nth-of-type(1) li:nth-child(1)`, pile2: `#${id} > .pile:nth-of-type(2)`, pile3: `#${id} > .pile:nth-of-type(3)` },
  check: `(() => { const d = document.querySelector("#${id}"); return { summary: d.querySelector("summary").textContent.trim(), piles: [...d.querySelectorAll(":scope > .pile")].map((p) => p.innerText.slice(0, 500)) }; })()`,
});
specs.push(
  {
    file: "lunar_piles_head.png", slide: null, path: Q + "&tab=data",
    shows: `Tab 'Where the data are' for '${QUERY}': the section heading and note, the header lines (the environment, the archive totals, the files that carry the names of the tests inside the ranges, two labels agree), the meaning of the three piles and the legend. The question blocks are closed.`,
    selectors: ["#piles .kicker", "#piles .section-head", "#piles-body .pile-header", "#piles-body .files-pick", "#piles-body .pile-meanings", "#piles-body .pile-legend"], padY: 4,
    prepare: `document.querySelectorAll("#piles-body > details.pile-need").forEach((d) => { d.open = false; }); window.scrollTo(0, 0);`,
    preparedNote: "The question blocks are closed for this capture; the header lines are as on the page.",
    boxes: { head: "#piles .section-head", header: "#piles-body .pile-header", meanings: "#piles-body .pile-meanings" },
    check: `({ header: (document.querySelector("#piles-body .pile-header") || {}).innerText, meanings: (document.querySelector("#piles-body .pile-meanings") || {}).innerText, legend: (document.querySelector("#piles-body .pile-legend") || {}).innerText })`,
  },
  PILES("lunar_piles_s1.png", "Extinction conditions", "cap-s1", 5, "counted droplet tests in NASA's tables; the files in the archive; no record in PSI"),
  PILES("lunar_piles_p1.png", "Flammability limit", "cap-p1", null, "no counted test inside the ranges; the files in the archive; no record in PSI"),
);

// The dashboard as a visitor sees it after the worked example: the request and how it was read, the three key
// figures, the notes, the five tabs and the head of the first result (slide 1).
specs.push({
  file: "dashboard.png", slide: 1, path: Q + "&tab=closest",
  shows: `The dashboard for '${QUERY}', from the top of the page: the app bar with the request, how the request was read, the three key figures, the notes for the environment, the five tabs with their one-line descriptions, and the first result card.`,
  selectors: ["#appbar", "header.masthead", "#request", "#glance", "#notes-band", "#tabs", "#top .kicker", "#top .section-head", CARD(1)], pad: 0, padY: 0,
  prepare: `window.scrollTo(0, 0);`,
  boxes: { appbar: "#appbar", request: "#request", glance: "#glance", tabs: "#tabs", head: "#top .section-head", card1: CARD(1) },
  check: `({ title: (document.querySelector("#request h1, #request h2, #request .req-title") || {}).textContent, tabs: [...document.querySelectorAll("#tabs a:not([hidden]) .tab-name")].map((e) => e.textContent.trim()), tab_lines: [...document.querySelectorAll("#tabs a:not([hidden]) .tab-desc")].map((e) => e.textContent.trim()), tiles: [...document.querySelectorAll("#glance > p:not(.typed-note)")].map((p) => p.innerText.replace(/\\s+/g, " ").trim().slice(0, 120)), first_card: (document.querySelector(${JSON.stringify(CARD(1))} + " h3") || {}).textContent })`,
});

// One conversation with the assistant on the local install, with the language model answering (slide 6).
// Taken only with DECK_LIVE=1 and DECK_ONLY=assistant_live.png, from the local assistant server
// (python3 -m ai.assistant.server), never from the static build: the public page runs no model.
const LIVE_FILE = "assistant_live.png";
const LIVE = process.env.DECK_LIVE === "1";
if (LIVE) {
  let health = null;
  try { health = await (await fetch(BASE + "api/health")).json(); } catch { /* handled below */ }
  if (!health || health.mode !== "live" || !health.model) { console.error("capture.mjs: DECK_LIVE=1 needs the local assistant server in live mode at " + BASE + " (python3 -m ai.assistant.server)"); stop(); process.exit(2); }
  specs.push({
    live_model: { name: health.model.name, maker: health.model.maker, license: health.model.license, digest_prefix: health.model.digest_prefix },
    file: LIVE_FILE, slide: 6, path: Q, width: 820,
    shows: `One conversation with the SI assistant on the local install, the language model ${health.model.name} answering: the request '${QUERY}' typed into the assistant's box, how the request was read (each value a button that changes it), the answer with its citation numbers, its label, and the box for a follow-up.`,
    selectors: ["#assistant"], pad: 0, padY: 0,
    prepare: `const sl = (m) => new Promise((r) => setTimeout(r, m));
      const A = document.querySelector("#assistant");
      for (let i = 0; i < 100 && !(A && A.querySelector(".as-form:not([hidden])") && document.querySelector("#as-input")); i++) await sl(200);
      document.querySelector("#as-input").value = ${JSON.stringify(QUERY)};
      A.querySelector(".as-form").requestSubmit();
      for (let i = 0; i < 1200; i++) { await sl(250); const t = [...A.querySelectorAll(".as-turn")].pop(); if (t && !t.classList.contains("as-working") && t.querySelector(".as-body") && t.querySelector(".as-body").children.length && !A.querySelector(".as-run")) break; }
      await sl(800);
      A.querySelectorAll(".as-chat, .as-panels").forEach((e) => { e.style.maxHeight = "none"; e.style.overflow = "visible"; });
      const turns = [...A.querySelectorAll(".as-turn")];
      turns[turns.length - 1].id = "cap-turn";
      window.scrollTo(0, 0);`,
    settle: 1500,
    preparedNote: "Taken from the local assistant server with the language model answering (live mode), not from the static build. The script typed the request into the assistant's box and waited for the answer; for this capture only, the scroll box of the conversation is opened so that nothing is cut.",
    boxes: { card: "#assistant", user: "#cap-turn .as-user", steps: "#cap-turn .as-steps", read: "#cap-turn .as-read", answer: "#cap-turn .as-answer", label: "#cap-turn .as-label", form: "#assistant .as-form" },
    check: `(() => { const A = document.querySelector("#assistant"); const t = document.querySelector("#cap-turn"); const g = (s) => { const e = t && t.querySelector(s); return e ? e.innerText : null; }; return { mode: A.getAttribute("data-mode"), model_chip: (document.querySelector("#model-chip") || {}).innerText, question: g(".as-user"), read_title: g(".as-read .as-h4"), read_hint: g(".as-read-hint"), values: t ? [...t.querySelectorAll(".as-read .as-chip")].map((c) => c.innerText.trim()) : [], editable_values: t ? t.querySelectorAll(".as-read .as-chip-edit").length : 0, answer: g(".as-answer"), by_model: !!(t && t.querySelector(".as-answer.as-by-model")), citations: t ? [...t.querySelectorAll(".as-answer *")].filter((e) => !e.children.length && /^\\d+$/.test(e.textContent.trim())).length : 0, label: g(".as-label"), gates: g(".as-gates"), answered: g(".as-answered"), follow_up_box: (document.querySelector("#as-input") || {}).placeholder }; })()`,
  });
}

// One recorded answer of the assistant (slide 6), only when the new recording is marked as ready.
const RECORDED_READY = existsSync(join(REPO, "ai", "assistant", "_runtime", "RECORDED_READY"));
if (RECORDED_READY) {
  let rec = null, conv = null;
  try { rec = await (await fetch(BASE + "assistant/recorded.json")).json(); conv = (rec.conversations || []).find((c) => c.id === RECORDED_CONVERSATION); } catch { /* handled below */ }
  const turn = conv && conv.turns && conv.turns[RECORDED_TURN - 1];
  const answer = turn && turn.response && turn.response.answer;
  if (!turn || !turn.message) notTaken.push({ file: "assistant_recorded.png", why: `assistant/recorded.json of the site has no conversation '${RECORDED_CONVERSATION}' with a turn ${RECORDED_TURN}` });
  else if (!answer || answer.origin !== "model" || !(answer.sentences || []).some((x) => x.origin === "model" && (x.facts || []).length))
    notTaken.push({ file: "assistant_recorded.png", why: `the answer of conversation '${RECORDED_CONVERSATION}', turn ${RECORDED_TURN}, is not written by the model with cited facts (origin: ${answer ? answer.origin : "none"}): choose another turn` });
  else specs.push({
    recorded_answer: { origin: answer.origin, sentences: answer.sentences.map((x) => ({ origin: x.origin, status: x.status, cites: x.facts })) },
    file: "assistant_recorded.png", slide: 6, path: "", optional: true, recorded_at: rec.recorded_at || null, recorded_model: rec.model || null,
    shows: `One recorded answer of the conversational assistant, replayed on the page (no model runs there): conversation '${RECORDED_CONVERSATION}', turn ${RECORDED_TURN}, the question '${turn.message}', the steps, the answer with its citation numbers, the 'Recorded on ...' label and the gate line.`,
    selectors: ["#assistant > h2", "#assistant .as-mode", "#assistant .as-chat"],
    prepare: `const sl = (m) => new Promise((r) => setTimeout(r, m));
      for (let i = 0; i < 100 && !document.querySelector("#assistant .as-examples:not([hidden])"); i++) await sl(200);
      const A = document.querySelector("#assistant");
      for (const m of ${JSON.stringify(conv.turns.slice(0, RECORDED_TURN).map((t) => t.message))}) {
        const before = A.querySelectorAll(".as-turn").length;
        document.querySelector("#as-input").value = m;
        A.querySelector(".as-form").requestSubmit();
        for (let i = 0; i < 200; i++) { await sl(200); const ts = A.querySelectorAll(".as-turn"); const b = ts.length > before && ts[ts.length - 1].querySelector(".as-body"); if (b && b.children.length && !A.querySelector(".as-run")) break; }
        await sl(600);
      }
      A.querySelectorAll(".as-chat, .as-panels").forEach((e) => { e.style.maxHeight = "none"; e.style.overflow = "visible"; });
      const turns = [...A.querySelectorAll(".as-turn")];
      turns.slice(0, -1).forEach((t) => { t.style.display = "none"; });
      turns[turns.length - 1].id = "cap-turn";
      window.scrollTo(0, 0);`,
    settle: 1500,
    preparedNote: "The recorded questions of the conversation up to the chosen turn were typed into the assistant's input; in recorded mode the page replays the recorded turn with that exact text (no model is called). For this capture only, the scroll box of the conversation is opened so that nothing is cut, and earlier turns are hidden.",
    boxes: { chat: "#assistant .as-chat", question: "#cap-turn .as-user", answer: "#cap-turn .as-answer", label: "#cap-turn .as-label", gates: "#cap-turn .as-gates" },
    check: `(() => { const A = document.querySelector("#assistant"); const t = [...A.querySelectorAll(".as-turn")].pop(); const g = (s) => { const e = t && t.querySelector(s); return e ? e.innerText : null; }; const ans = g(".as-answer") || ""; return { mode: (A.querySelector(".as-mode") || {}).textContent, label: g(".as-label"), answer: ans, citations: t ? [...t.querySelectorAll(".as-answer *")].filter((e) => !e.children.length && /^\\d+$/.test(e.textContent.trim())).length : 0, question: g(".as-user"), by_model: !!(t && t.querySelector(".as-answer.as-by-model")), notice: g(".as-notice"), gates: g(".as-gates") }; })()`,
  });
} else {
  notTaken.push({ file: "assistant_recorded.png", why: "ai/assistant/_runtime/RECORDED_READY does not exist: the new recording of the assistant is not finished, so slide 6 shows no recorded answer" });
}

const only = LIVE ? [LIVE_FILE] : (process.env.DECK_ONLY ? process.env.DECK_ONLY.split(",").map((s) => s.trim()).filter(Boolean) : null);
if (only) { const unknown = only.filter((f) => !specs.some((s) => s.file === f)); if (unknown.length) { console.error("capture.mjs: DECK_ONLY names no capture: " + unknown.join(", ") + ". Known: " + specs.map((s) => s.file).join(", ")); process.exit(2); } }
let failed = 0;
for (const s of specs) {
  if (only && !only.includes(s.file)) continue;
  try { await capture(s); if (s.live_model) Object.assign(manifest[manifest.length - 1], { live: true, live_model: s.live_model, note: "capture of the team's own page on the local install; the answer in it was written by the local language model" }); if (s.recorded_answer) Object.assign(manifest[manifest.length - 1], { recorded_at: s.recorded_at, recorded_model: s.recorded_model, conversation: RECORDED_CONVERSATION, turn: RECORDED_TURN, recorded_answer: s.recorded_answer }); }
  catch (e) {
    if (s.optional) { notTaken.push({ file: s.file, why: String(e.message || e) }); console.error("capture.mjs: optional capture not taken:", s.file, "-", e.message || e); }
    else { failed++; console.error("capture.mjs: FAILED", s.file, "-", e.message || e); }
  }
}

// ------------------------------------------------------------------ the manifest (img/captures.json)
const mpath = join(OUT, "captures.json");
let kept = [];
if (existsSync(mpath)) {
  // a run of some captures keeps the other entries; the live capture's entry is kept by every run that does not retake it
  const names = [...specs.map((s) => s.file), ...(LIVE ? (() => { try { return JSON.parse(readFileSync(mpath, "utf8")).captures.map((c) => c.file); } catch { return []; } })() : [])];
  try { kept = JSON.parse(readFileSync(mpath, "utf8")).captures.filter((c) => !manifest.some((m) => m.file === c.file) && existsSync(join(OUT, c.file)) && (c.file === LIVE_FILE || (only && names.includes(c.file)))); } catch { kept = []; }
}
const order = specs.map((s) => s.file);
const captures = [...kept, ...manifest].sort((a, b) => order.indexOf(a.file) - order.indexOf(b.file));
const configs = [...new Set(captures.map((c) => c.scoring_config))];
const out = {
  _meta: {
    what: "Captures of the team's own page (Fire Evidence Explorer) for the seven-slide deck. Not AI-generated images; no NASA logo appears in any of them.",
    "AI-generated": false,
    note: "capture of the team's own page",
    taken_by: `docs/submission/deck/capture.mjs (AI-generated code, Claude), headless ${version.Browser || "Google Chrome"} over the DevTools protocol; no library.`,
    written_at: new Date().toISOString(),
    git_commit: commit,
    scoring_config: configs.length === 1 ? configs[0] : null,
    scoring_configs_of_the_captures: configs,
    page_build: { source: "web/build.py run in a scratch copy of the working tree (docs/submission/deck/refresh.sh); the repository's own web/dist was not touched.", served_from: BASE, built_at: site.built_at || null },
    query: QUERY,
    viewport: { width: WIDTH, device_scale_factor: SCALE, color_scheme: "light" },
    fonts: `The page's own fonts (${PAGE_FONTS.join(", ")}; SIL Open Font License) were loaded from Google Fonts, as web/index.html does. Chrome could reach 127.0.0.1 and ${FONT_HOSTS.join(", ")} only; every other host name was unresolvable.`,
    recorded_assistant: { conversation: RECORDED_CONVERSATION, turn: RECORDED_TURN, recorded_ready: RECORDED_READY },
    not_taken: notTaken,
  },
  captures,
};
if (!failed) { writeFileSync(mpath, JSON.stringify(out, null, 2) + "\n"); console.log("manifest", mpath, `(${captures.length} captures, scoring config ${configs.join(", ")})`); }
else console.error(`capture.mjs: ${failed} capture(s) failed; img/captures.json was not rewritten`);
process.exit(failed ? 1 : 0);
