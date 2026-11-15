// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14). Takes the dashboard screenshots, the demo GIF and the
// link-preview image for the project page (task U5).
//
// Usage (the live site, or a local build served on a port):
//   node web/capture_media.mjs [https://choidol0208.github.io/NASA_RAPID/] [out_dir]
// Needs Playwright with Chromium (NODE_PATH=$(npm root -g) for a global install) and ffmpeg.
// Writes into web/media/ unless out_dir is given. Sections that are absent (for example the
// evidence map before its data file exists) are skipped and reported.
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const { chromium } = createRequire(import.meta.url)("playwright"); // require() also honours NODE_PATH
const BASE = process.argv[2] || "https://choidol0208.github.io/NASA_RAPID/";
const OUT = process.argv[3] || join(dirname(fileURLToPath(import.meta.url)), "media");
const FRAMES = join(OUT, ".frames");
mkdirSync(OUT, { recursive: true });
const skipped = [];
// CAPTURE_ONLY=slide3_lunar_result.png,og.png retakes only the named files (default: all)
const ONLY = (process.env.CAPTURE_ONLY || "").split(",").map((s) => s.trim()).filter(Boolean);
const want = (name) => !ONLY.length || ONLY.includes(name);

const browser = await chromium.launch();

async function open(page, q) {
  await page.goto(BASE + "?q=" + encodeURIComponent(q));
  await page.waitForFunction(() => document.querySelector("#glance") && !document.querySelector("#glance").hidden, null, { timeout: 30000 });
  await page.waitForTimeout(1500);
}

// The page is over 29,000 px tall at 1280 px since the results-first and three-piles sections: a 2x full-page
// capture of it does not finish in 30 s. For one capture only, hide the page blocks that hold none of the
// captured elements, so the page is short; the captured blocks keep their width (the layout is one column).
const isolate = (sels) => {
  const keep = sels.map((s) => document.querySelector(s)).filter(Boolean);
  for (const b of document.querySelectorAll("body > *, main > *")) {
    if (b.tagName !== "SCRIPT" && !keep.some((k) => b.contains(k))) b.style.display = "none";
  }
};

async function shot(name, q, { width = 1280, height = 800, scale = 2, section = null, open: openSel = null, full = false, clip = null, maxHeight = 0 } = {}) {
  if (!want(name)) return;
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: scale });
  await open(page, q);
  if (openSel) await page.evaluate((s) => document.querySelectorAll(s).forEach((d) => { d.open = true; }), openSel);
  await page.waitForTimeout(openSel ? 1500 : 200);
  if (section) {
    const el = await page.$(section);
    const visible = el && (await el.evaluate((e) => !e.closest("[hidden]") && e.getBoundingClientRect().height > 30));
    if (!visible) { skipped.push(`${name} (${section} not on the page)`); await page.close(); return; }
    await page.evaluate(isolate, [section]);
    await page.waitForTimeout(300);
    // a page clip, not an element screenshot: a section thousands of pixels tall never passes the element "stable" wait
    const box = await el.evaluate((e, maxH) => {
      const r = e.getBoundingClientRect();
      return { x: Math.max(0, r.left), y: r.top + window.scrollY, width: Math.min(r.width, document.documentElement.clientWidth), height: maxH ? Math.min(r.height, maxH) : r.height };
    }, maxHeight);
    await page.screenshot({ path: join(OUT, name), clip: box, fullPage: true });
  } else {
    await page.screenshot({ path: join(OUT, name), fullPage: full, clip: clip || undefined });
  }
  await page.close();
  console.log("wrote", name);
}

// Stills (PNG, well under 10 MB each), in the page's order: Find, Compare, Interpret.
await shot("01_iss_first_screen.png", "ISS");
await shot("02_lunar_first_screen.png", "lunar habitat");
await shot("03_compare_iss_lunar.png", "lunar habitat", { section: "#compare" });
await shot("04_lunar_evidence_map.png", "lunar habitat", { section: "#stops-map .emap-wrap" });
await shot("05_lunar_constraints.png", "lunar habitat", { section: "#answers:not([hidden]), #shown:not([hidden])", open: "#answers details.ans:first-of-type", maxHeight: 1600 });
await shot("06_lunar_coverage_solid.png", "lunar habitat cotton fabric", { section: "#coverage .cov-block" });
await shot("07_lunar_phone.png", "lunar habitat", { width: 390, height: 844, scale: 3 });
// Link preview (Open Graph): 1200 x 630, the first screen of the lunar habitat query.
await shot("og.png", "lunar habitat", { width: 1200, height: 630, scale: 1 });

// Slide captures (pm request 1630): several elements in one picture, at 2x so they are over 1600 px wide.
async function unionShot(name, q, sels, prepare = null) {
  if (!want(name)) return;
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
  await open(page, q);
  if (prepare) { await page.evaluate(prepare); await page.waitForTimeout(1000); }
  await page.evaluate(isolate, sels);
  await page.waitForTimeout(300);
  const clip = await page.evaluate((sels) => {
    const rs = sels.map((s) => document.querySelector(s)).filter((e) => e && !e.closest("[hidden]")).map((e) => e.getBoundingClientRect());
    if (!rs.length) return null;
    const pad = 14, sy = window.scrollY, cw = document.documentElement.clientWidth;
    const x0 = Math.max(0, Math.min(...rs.map((r) => r.left)) - pad), x1 = Math.min(cw, Math.max(...rs.map((r) => r.right)) + pad);
    const y0 = Math.max(0, Math.min(...rs.map((r) => r.top)) + sy - pad), y1 = Math.max(...rs.map((r) => r.bottom)) + sy + pad;
    return { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
  }, sels);
  if (!clip) { skipped.push(`${name} (none of ${sels.join(", ")} on the page)`); await page.close(); return; }
  await page.screenshot({ path: join(OUT, name), clip, fullPage: true });
  await page.close();
  console.log("wrote", name, `${Math.round(clip.width * 2)}x${Math.round(clip.height * 2)}`);
}
await unionShot("slide1_top.png", "ISS", ["header.masthead", "section.ask"]);
await unionShot("slide2_iss_result.png", "ISS", ["#top .kicker", "#top .section-head", "#results > li:first-child"]);
await unionShot("slide3_iss_needs.png", "ISS", ["#needs .kicker", "#needs .section-head", "#needs-body .table-wrap"], () => {
  // the slide shows the table alone: hide the blocks that sit between the heading and the table, for this capture only
  for (const s of ["#needs > p.intro", "#points", "#compare", "#scenario-frame", "#needs-body > .scroll-hint"]) {
    const e = document.querySelector(s);
    if (e) e.style.display = "none";
  }
});
await unionShot("slide7_iss_tests.png", "ISS", ["#tests .section-head", "#tests-body .tests-table", "#capture-tests-links"], () => {
  const d = document.querySelector("#tests-body details.tests-list");
  if (d) d.open = true;
  const notes = [...document.querySelectorAll("#tests-body > p.gap")];
  if (notes.length) notes[notes.length - 1].id = "capture-tests-links";
});
// slides 3, 5 and 6 of docs/submission/slides_outline.md ("Captures" table)
await unionShot("slide3_lunar_result.png", "lunar habitat", ["#top .kicker", "#top .section-head", "#results > li:nth-child(3)"], () => {
  // the slide asks for the score note, each card's reason line and largest gap: the long team note, the raw-file
  // line and the record summary are left out of this capture only (as the slide 3 ISS capture leaves out its intro)
  for (const e of document.querySelectorAll("#results > li > .ai-note, #results > li > .raw-line, #results > li > details.more")) e.style.display = "none";
});
await unionShot("slide5_lunar_piles.png", "lunar habitat", ["#piles .section-head", "#capture-pile-p1", "#capture-pile-s1"], () => {
  // the slide shows the extinction conditions (S1) and flammability limit (P1) questions open, the others closed
  for (const d of document.querySelectorAll("#piles-body details.pile-need")) {
    const s = d.querySelector("summary b")?.textContent || "";
    d.open = /\((P1|S1)\)$/.test(s);
    if (s.endsWith("(P1)")) d.id = "capture-pile-p1";
    if (s.endsWith("(S1)")) d.id = "capture-pile-s1";
  }
});
await unionShot("slide6_ai_use.png", "lunar habitat", ["#ai-use-title", "#ai-use > p", "#ai-use-body"]);

// GIF of the demo story: ISS, then lunar habitat, the comparison, the evidence map.
if (want("demo_iss_to_lunar.gif")) {
if (existsSync(FRAMES)) rmSync(FRAMES, { recursive: true });
mkdirSync(FRAMES);
const page = await browser.newPage({ viewport: { width: 1100, height: 720 }, deviceScaleFactor: 1 });
let n = 0;
const frame = async (hold = 1) => { for (let i = 0; i < hold; i++) await page.screenshot({ path: join(FRAMES, `f${String(n++).padStart(4, "0")}.png`) }); };
const typeQuery = async (q) => {
  await page.fill("#q", "");
  for (const ch of q) { await page.type("#q", ch); await frame(1); }
  await page.click("button[type=submit]");
  await page.waitForTimeout(700);
  await frame(10);
};
const scrollTo = async (sel, steps = 8) => {
  const ok = await page.evaluate((s) => { const e = document.querySelector(s); return Boolean(e && !e.closest("[hidden]")); }, sel);
  if (!ok) return false;
  const y0 = await page.evaluate(() => window.scrollY);
  const y1 = await page.evaluate((s) => document.querySelector(s).getBoundingClientRect().top + window.scrollY - 20, sel);
  for (let i = 1; i <= steps; i++) { await page.evaluate((y) => window.scrollTo(0, y), y0 + ((y1 - y0) * i) / steps); await frame(1); }
  return true;
};
await page.goto(BASE);
await page.waitForFunction(() => document.querySelector("#glance") && !document.querySelector("#glance").hidden, null, { timeout: 30000 });
await page.waitForTimeout(1000);
await frame(4);
await typeQuery("ISS");
await frame(8);
await page.evaluate(() => window.scrollTo(0, 0));
await typeQuery("lunar habitat");
await frame(10);
if (await scrollTo("#compare")) await frame(18);
if (await scrollTo("#stops-map .emap-wrap")) await frame(22);
else if (await scrollTo("#coverage")) await frame(18);
await page.close();

const gif = join(OUT, "demo_iss_to_lunar.gif");
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", "6", "-i", join(FRAMES, "f%04d.png"),
  "-vf", "scale=880:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
  gif]);
rmSync(FRAMES, { recursive: true });
console.log("wrote", gif);
}
await browser.close();
if (skipped.length) console.log("skipped:", skipped.join("; "));
