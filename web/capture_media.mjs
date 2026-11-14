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

const browser = await chromium.launch();

async function open(page, q) {
  await page.goto(BASE + "?q=" + encodeURIComponent(q));
  await page.waitForFunction(() => document.querySelector("#glance") && !document.querySelector("#glance").hidden, null, { timeout: 30000 });
  await page.waitForTimeout(1500);
}

async function shot(name, q, { width = 1280, height = 800, scale = 2, section = null, open: openSel = null, full = false, clip = null } = {}) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: scale });
  await open(page, q);
  if (openSel) await page.evaluate((s) => document.querySelectorAll(s).forEach((d) => { d.open = true; }), openSel);
  await page.waitForTimeout(openSel ? 1500 : 200);
  if (section) {
    const el = await page.$(section);
    const visible = el && (await el.evaluate((e) => !e.closest("[hidden]") && e.getBoundingClientRect().height > 30));
    if (!visible) { skipped.push(`${name} (${section} not on the page)`); await page.close(); return; }
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(200);
    await el.screenshot({ path: join(OUT, name) });
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
await shot("05_lunar_constraints.png", "lunar habitat", { section: "#answers:not([hidden]), #shown:not([hidden])", open: "#answers details.ans:first-of-type" });
await shot("06_lunar_coverage_solid.png", "lunar habitat cotton fabric", { section: "#coverage .cov-block" });
await shot("07_lunar_phone.png", "lunar habitat", { width: 390, height: 844, scale: 3 });
// Link preview (Open Graph): 1200 x 630, the first screen of the lunar habitat query.
await shot("og.png", "lunar habitat", { width: 1200, height: 630, scale: 1 });

// GIF of the demo story: ISS, then lunar habitat, the comparison, the evidence map.
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
await browser.close();

const gif = join(OUT, "demo_iss_to_lunar.gif");
execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", "6", "-i", join(FRAMES, "f%04d.png"),
  "-vf", "scale=880:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
  gif]);
rmSync(FRAMES, { recursive: true });
console.log("wrote", gif);
if (skipped.length) console.log("skipped:", skipped.join("; "));
